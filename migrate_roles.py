import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

technicians = User.objects.filter(role='TECHNICIAN')
for u in technicians:
    u.role = 'RESPONDER'
    u.job_title = 'IT Technician'
    u.save()
    print(f"Migrated {u.username} to RESPONDER with title IT Technician")

analysts = User.objects.filter(role='ANALYST')
for u in analysts:
    u.role = 'RESPONDER'
    u.job_title = 'Security Analyst'
    u.save()
    print(f"Migrated {u.username} to RESPONDER with title Security Analyst")

managers = User.objects.filter(role='MANAGER')
for u in managers:
    u.job_title = 'System Manager'
    u.save()
    print(f"Updated {u.username} title to System Manager")
