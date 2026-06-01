from django.db import models
from django.conf import settings
import logging

audit_logger = logging.getLogger('audit')

class Ticket(models.Model):
    TICKET_TYPE_CHOICES = (
        ('HELPDESK', 'IT Helpdesk Ticket'),
        ('INCIDENT', 'Security Incident'),
    )
    
    NIST_STAGE_CHOICES = (
        ('PREPARATION', 'Preparation'),
        ('DETECTION', 'Detection & Analysis'),
        ('CONTAINMENT', 'Containment'),
        ('RECOVERY', 'Eradication & Recovery'),
        ('POST_INCIDENT', 'Post-Incident Activity'),
    )

    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES, default='HELPDESK')
    nist_stage = models.CharField(max_length=20, choices=NIST_STAGE_CHOICES, default='PREPARATION')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    attachment = models.ImageField(upload_to='incident_evidence/', blank=True, null=True)
    
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_tickets')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    
    is_closed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.ticket_type}] {self.title} - {self.nist_stage}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not is_new:
            old_ticket = Ticket.objects.get(pk=self.pk)
            changes = []
            if old_ticket.nist_stage != self.nist_stage:
                changes.append(f"Stage changed from {old_ticket.nist_stage} to {self.nist_stage}")
            if old_ticket.is_closed != self.is_closed:
                changes.append(f"Status changed to {'Closed' if self.is_closed else 'Open'}")
            
            if changes:
                audit_logger.info(f"[Reporter: {self.reporter.username}] Ticket {self.pk} updated: {', '.join(changes)}")
        
        super().save(*args, **kwargs)
        
        if is_new:
            audit_logger.info(f"[Reporter: {self.reporter.username}] New Ticket created: ID {self.pk}, Type {self.ticket_type}")

class TicketUpdate(models.Model):
    """Stores detailed chain of custody / updates"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='updates')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    new_stage = models.CharField(max_length=20, choices=Ticket.NIST_STAGE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update for Ticket {self.ticket.id} by {self.author.username}"
