from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Ticket
from .serializers import TicketSerializer
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('-created_at')
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_technician:
            return Ticket.objects.all().order_by('-created_at')
        return Ticket.objects.filter(reporter=user).order_by('-created_at')

    @method_decorator(ratelimit(key='user', rate='5/m', method='POST', block=True))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reporter=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        # Additional logic for logging or RBAC can go here
        serializer.save()

class IncidentMetricsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        if user.role == 'MANAGER' or user.is_staff:
            queryset = Ticket.objects.all()
        else:
            queryset = Ticket.objects.filter(reporter=user)
            
        total_incidents = queryset.filter(ticket_type='INCIDENT').count()
        total_tickets = queryset.count()
        active_tickets = queryset.filter(is_closed=False).count()
        critical_tickets = queryset.filter(priority='CRITICAL', is_closed=False).count()
        
        return Response({
            'total_incidents': total_incidents,
            'total_tickets': total_tickets,
            'active_tickets': active_tickets,
            'critical_tickets': critical_tickets,
        })
