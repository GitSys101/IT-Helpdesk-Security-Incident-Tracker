from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial test users and roles.'

    def handle(self, *args, **kwargs):
        roles_and_users = [
            ('admin_manager', 'managerpass', 'MANAGER'),
            ('tech_user', 'techpass', 'TECHNICIAN'),
            ('sec_analyst', 'analystpass', 'ANALYST'),
            ('standard_user', 'userpass', 'USER'),
        ]

        for username, password, role in roles_and_users:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password, role=role)
                if role == 'MANAGER':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created {role} user: {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already exists.'))
                
        self.stdout.write(self.style.SUCCESS('Role seeding completed.'))
