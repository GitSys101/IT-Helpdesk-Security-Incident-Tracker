from django import forms
from django.forms import inlineformset_factory
from .models import Ticket, TicketAttachment

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'ticket_type', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

TicketAttachmentFormSet = inlineformset_factory(
    Ticket, 
    TicketAttachment, 
    fields=('file',), 
    extra=1, 
    can_delete=True,
    widgets={
        'file': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    }
)
