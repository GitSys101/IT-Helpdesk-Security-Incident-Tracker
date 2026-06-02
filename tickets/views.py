from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Ticket, TicketUpdate
from .forms import TicketForm, TicketAttachmentFormSet
from django.db.models import Q
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.views.decorators.http import require_POST
import logging

audit_logger = logging.getLogger('audit')
import os
from django.conf import settings

def is_manager(user):
    return user.is_authenticated and user.role == 'MANAGER'

def is_technician(user):
    return user.is_authenticated and (user.role in ['TECHNICIAN', 'ANALYST', 'MANAGER'])


class DashboardSummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'tickets/dashboard_summary.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if is_technician(user):
            qs = Ticket.objects.all()
            context['my_assigned_tickets'] = qs.filter(assigned_to=user, is_closed=False).count()
        else:
            qs = Ticket.objects.filter(reporter=user)
            
        context['total_tickets'] = qs.count()
        context['active_tickets'] = qs.filter(is_closed=False).count()
        context['critical_tickets'] = qs.filter(priority__in=['HIGH', 'CRITICAL'], is_closed=False).count()
        context['resolved_tickets'] = qs.filter(is_closed=True).count()
        context['recent_tickets'] = qs.order_by('-created_at')[:5]
        return context

class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        queryset = Ticket.objects.all().order_by('-created_at')
        
        # Filtering
        q = self.request.GET.get('q')
        type_filter = self.request.GET.get('type')
        stage_filter = self.request.GET.get('stage')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if type_filter:
            queryset = queryset.filter(ticket_type=type_filter)
        if stage_filter:
            queryset = queryset.filter(nist_stage=stage_filter)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date + ' 23:59:59')
            
        status_filter = self.request.GET.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(is_closed=False)
        elif status_filter == 'resolved':
            queryset = queryset.filter(is_closed=True)
            
        priority_filter = self.request.GET.get('priority')
        if priority_filter == 'critical':
            queryset = queryset.filter(priority__in=['HIGH', 'CRITICAL'], is_closed=False)
            
        reporter_filter = self.request.GET.get('reporter')
        if reporter_filter == 'me':
            queryset = queryset.filter(reporter=user)
        elif reporter_filter == 'assigned_to_me':
            queryset = queryset.filter(assigned_to=user)
        elif not is_technician(user):
            queryset = queryset.filter(reporter=user)
            
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sort_fields = ['id', 'ticket_type', 'title', 'nist_stage', 'priority', 'is_closed', 'created_at',
                             '-id', '-ticket_type', '-title', '-nist_stage', '-priority', '-is_closed', '-created_at']
        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)
            
        return queryset

@require_POST
@login_required
@user_passes_test(is_manager)
def reopen_ticket(request, pk):
    from django.shortcuts import get_object_or_404
    ticket = get_object_or_404(Ticket, pk=pk)
    if ticket.is_closed:
        ticket.is_closed = False
        ticket.nist_stage = 'RECOVERY'
        ticket.save()
        
        TicketUpdate.objects.create(
            ticket=ticket,
            author=request.user,
            comment="Ticket re-opened by Manager.",
            new_stage='RECOVERY'
        )
        messages.success(request, f"Ticket #{ticket.id} has been reopened.")
    return redirect('ticket_detail', pk=pk)

@login_required
@user_passes_test(is_manager)
def bulk_close_tickets(request):
    if request.method == 'POST':
        ticket_ids = request.POST.getlist('ticket_ids')
        if ticket_ids:
            updated_count = Ticket.objects.filter(id__in=ticket_ids).update(is_closed=True, nist_stage='POST_INCIDENT')
            audit_logger.info(f"Bulk Close: {updated_count} tickets closed by {request.user.username}. IDs: {ticket_ids}")
            messages.success(request, f"Successfully closed {updated_count} tickets.")
        else:
            messages.warning(request, "No tickets selected.")
    return redirect('ticket_list')

@method_decorator(ratelimit(key='user', rate='5/m', method='POST', block=True), name='post')
class TicketCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    def test_func(self):
        # Managers oversee the system, they do not create tickets.
        return not is_manager(self.request.user)

    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TicketAttachmentFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = TicketAttachmentFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            form.instance.reporter = self.request.user
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            ticket_title = self.object.title
            audit_logger.info(f"Ticket Create: Ticket #{self.object.id} ('{ticket_title}') was created by {self.request.user.username}.")
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'

    def get_queryset(self):
        user = self.request.user
        if is_technician(user):
            return Ticket.objects.all()
        return Ticket.objects.filter(reporter=user)

class TicketUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ticket
    fields = ['nist_stage', 'assigned_to']
    template_name = 'tickets/ticket_form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # Only allow assigning to IT Staff (exclude End Users and Managers)
        form.fields['assigned_to'].queryset = User.objects.filter(role__in=['TECHNICIAN', 'ANALYST'])
        
        # Enforce Linear NIST Stage Progression
        current_stage = self.object.nist_stage
        stages = [s[0] for s in Ticket.NIST_STAGE_CHOICES]
        try:
            current_index = stages.index(current_stage)
            # Only allow selecting the current stage or stages after it
            allowed_stages = Ticket.NIST_STAGE_CHOICES[current_index:]
            # Prevent manual selection of POST_INCIDENT (reserved for Manager Bulk Close)
            allowed_stages = [s for s in allowed_stages if s[0] != 'POST_INCIDENT']
            form.fields['nist_stage'].choices = allowed_stages
        except ValueError:
            pass
            
        # Managers are for oversight and assignment, not fixing things!
        if is_manager(self.request.user):
            form.fields['nist_stage'].disabled = True
            
        return form
    
    def test_func(self):
        user = self.request.user
        if not is_technician(user):
            return False
            
        ticket = self.get_object()
        # If ticket is unassigned, any IT staff can claim it
        if ticket.assigned_to is None:
            return True
            
        # Managers can override and edit any ticket
        if is_manager(user):
            return True
            
        # Technicians can only edit their own assigned tickets
        return ticket.assigned_to == user
    
    def get_success_url(self):
        return reverse_lazy('ticket_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        comment = self.request.POST.get('comment', 'Status updated via dashboard.')
        TicketUpdate.objects.create(
            ticket=self.object,
            author=self.request.user,
            comment=comment,
            new_stage=form.cleaned_data['nist_stage']
        )
        return super().form_valid(form)

class AuditLogView(LoginRequiredMixin, TemplateView):
    template_name = 'tickets/audit_logs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_file_path = os.path.join(settings.BASE_DIR, 'audit.log')
        logs = []
        user = self.request.user
        
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as f:
                all_logs = f.readlines()
                if user.role == 'MANAGER' or user.is_staff:
                    raw_logs = all_logs
                else:
                    raw_logs = [line for line in all_logs if user.username in line]
                    
                # Parse logs robustly instead of relying on string indices
                for line in raw_logs:
                    parts = line.strip().split(' ', 3) # Split into LEVEL, DATE, TIME, MESSAGE
                    if len(parts) >= 4:
                        level = parts[0]
                        timestamp = f"{parts[1]} {parts[2]}"
                        message = parts[3]
                        logs.append({'level': level, 'timestamp': timestamp, 'message': message})
                    else:
                        logs.append({'level': 'LOG', 'timestamp': 'Unknown', 'message': line.strip()})
                        
        # Return last 100 logs reversed
        context['logs'] = list(reversed(logs))[:100]
        return context

class TicketUserEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'
    
    def test_func(self):
        ticket = self.get_object()
        return self.request.user == ticket.reporter and ticket.nist_stage == 'PREPARATION' and not ticket.is_closed
        
    def get_success_url(self):
        return reverse_lazy('ticket_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TicketAttachmentFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['formset'] = TicketAttachmentFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            return self.form_invalid(form)

        ticket_id = self.object.id
        old_ticket = Ticket.objects.get(pk=ticket_id)
        
        changes = []
        if old_ticket.title != form.cleaned_data.get('title'):
            changes.append(f"Title: '{old_ticket.title}' -> '{form.cleaned_data.get('title')}'")
        if old_ticket.description != form.cleaned_data.get('description'):
            changes.append(f"Description modified")
        if old_ticket.ticket_type != form.cleaned_data.get('ticket_type'):
            changes.append(f"Type: '{old_ticket.get_ticket_type_display()}' -> '{dict(Ticket.TICKET_TYPE_CHOICES).get(form.cleaned_data.get('ticket_type'))}'")
        if old_ticket.priority != form.cleaned_data.get('priority'):
            changes.append(f"Priority: '{old_ticket.get_priority_display()}' -> '{dict(Ticket.PRIORITY_CHOICES).get(form.cleaned_data.get('priority'))}'")
            
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        
        if changes:
            changes_str = ", ".join(changes)
            audit_logger.info(f"Ticket Edit: Ticket #{ticket_id} updated by {self.request.user.username}. Changes: {changes_str}")
        else:
            audit_logger.info(f"Ticket Edit: Ticket #{ticket_id} ('{self.object.title}') was saved by {self.request.user.username} with no visible changes.")
            
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())

class TicketDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ticket
    template_name = 'tickets/ticket_confirm_delete.html'
    success_url = reverse_lazy('ticket_list')

    def test_func(self):
        ticket = self.get_object()
        return self.request.user == ticket.reporter and ticket.nist_stage == 'PREPARATION' and not ticket.is_closed

    def form_valid(self, form):
        ticket_id = self.object.id
        ticket_title = self.object.title
        ticket_type = self.object.get_ticket_type_display()
        response = super().form_valid(form)
        audit_logger.info(f"Ticket Delete: Ticket #{ticket_id} ('{ticket_title}' - {ticket_type}) was deleted by {self.request.user.username}.")
        return response
