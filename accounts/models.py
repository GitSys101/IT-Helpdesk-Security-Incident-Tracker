from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('MANAGER', 'System Manager'),
        ('RESPONDER', 'Incident Responder'),
        ('USER', 'End User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    job_title = models.CharField(max_length=100, default='Employee')
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_manager(self):
        return self.role == 'MANAGER'
    

    @property
    def is_technician(self):
        return self.role in ['RESPONDER', 'MANAGER']
