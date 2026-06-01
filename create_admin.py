import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

common_password = 'password123'

# Create Admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', common_password)
    print("Admin user created.")

# Create Managers
managers = ['admin_manager', 'manager1']
for m in managers:
    if not User.objects.filter(username=m).exists():
        user = User.objects.create_user(m, f'{m}@example.com', common_password)
        user.role = 'MANAGER'
        user.job_title = 'System Manager'
        user.save()
        print(f"Manager {m} created.")

# Create Responders (Technicians & Analysts)
responders = [
    ('tech1', 'IT Technician'),
    ('tech_user', 'IT Technician'),
    ('analyst1', 'Security Analyst'),
    ('sec_analyst', 'Security Analyst')
]
for r_name, r_title in responders:
    if not User.objects.filter(username=r_name).exists():
        user = User.objects.create_user(r_name, f'{r_name}@example.com', common_password)
        user.role = 'RESPONDER'
        user.job_title = r_title
        user.save()
        print(f"Responder {r_name} created.")
    
# Create Demo Users
users = ['user1', 'user2']
for u in users:
    if not User.objects.filter(username=u).exists():
        user = User.objects.create_user(u, f'{u}@example.com', common_password)
        user.role = 'USER'
        user.job_title = 'Staff'
        user.save()
        print(f"Regular user {u} created.")
