from django.contrib import admin
from .models import Ticket, TicketUpdate

@admin.action(description='Bulk close selected tickets')
def bulk_close(modeladmin, request, queryset):
    queryset.update(is_closed=True, nist_stage='POST_INCIDENT')

class TicketUpdateInline(admin.TabularInline):
    model = TicketUpdate
    extra = 1

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_type', 'title', 'nist_stage', 'priority', 'reporter', 'is_closed', 'created_at')
    list_filter = ('ticket_type', 'nist_stage', 'priority', 'is_closed')
    search_fields = ('title', 'description')
    actions = [bulk_close]
    inlines = [TicketUpdateInline]
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.reporter = request.user
        super().save_model(request, obj, form, change)

@admin.register(TicketUpdate)
class TicketUpdateAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'new_stage', 'created_at')
