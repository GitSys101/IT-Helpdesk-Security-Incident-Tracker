from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import TicketViewSet, IncidentMetricsAPIView
from .views import DashboardSummaryView, TicketListView, TicketCreateView, TicketDetailView, TicketUpdateView, bulk_close_tickets, AuditLogView, TicketUserEditView, TicketDeleteView, reopen_ticket
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/metrics/', IncidentMetricsAPIView.as_view(), name='api_metrics'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # UI URLs
    path('', DashboardSummaryView.as_view(), name='dashboard'),
    path('tickets/', TicketListView.as_view(), name='ticket_list'),
    path('ticket/new/', TicketCreateView.as_view(), name='ticket_create'),
    path('ticket/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('ticket/<int:pk>/update/', TicketUpdateView.as_view(), name='ticket_update'),
    path('ticket/<int:pk>/user-edit/', TicketUserEditView.as_view(), name='ticket_user_edit'),
    path('ticket/<int:pk>/delete/', TicketDeleteView.as_view(), name='ticket_delete'),
    path('ticket/<int:pk>/reopen/', reopen_ticket, name='ticket_reopen'),
    path('ticket/bulk-close/', bulk_close_tickets, name='bulk_close'),
    path('audit-logs/', AuditLogView.as_view(), name='audit_logs'),
]
