from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from tickets.models import Ticket, TicketUpdate
import random

class Command(BaseCommand):
    help = 'Populates the database with dummy data for NIST-compliant IT Helpdesk & Security Incident Tracker'

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning database...")
        Ticket.objects.all().delete()
        # Keep admin, delete other dummy users if they exist
        CustomUser.objects.exclude(username='admin').delete()

        self.stdout.write("Creating users...")
        manager = CustomUser.objects.create_user(
            username='manager1', password='password123', role='MANAGER', 
            employee_id='EMP001', department='IT Management'
        )
        tech = CustomUser.objects.create_user(
            username='tech1', password='password123', role='TECHNICIAN', 
            employee_id='EMP002', department='IT Support'
        )
        analyst = CustomUser.objects.create_user(
            username='analyst1', password='password123', role='ANALYST', 
            employee_id='EMP003', department='Cybersecurity'
        )
        user1 = CustomUser.objects.create_user(
            username='user1', password='password123', role='USER', 
            employee_id='EMP004', department='Marketing'
        )
        user2 = CustomUser.objects.create_user(
            username='user2', password='password123', role='USER', 
            employee_id='EMP005', department='Finance'
        )

        users = [user1, user2]
        staff = [tech, analyst, manager]

        tickets_data = [
            {
                'title': 'Slow Internet in Marketing Dept',
                'description': 'The wifi in the north wing has been intermittent since this morning.',
                'ticket_type': 'HELPDESK',
                'nist_stage': 'PREPARATION',
                'priority': 'LOW',
                'reporter': user1,
                'assigned_to': tech,
            },
            {
                'title': 'Suspected Phishing Email - HR',
                'description': 'Multiple employees received an email asking for password resets. Possible credential harvesting.',
                'ticket_type': 'INCIDENT',
                'nist_stage': 'DETECTION',
                'priority': 'HIGH',
                'reporter': user2,
                'assigned_to': analyst,
            },
            {
                'title': 'Ransomware Alert - Server 04',
                'description': 'Encrypted files detected on the file server. Immediate containment required.',
                'ticket_type': 'INCIDENT',
                'nist_stage': 'CONTAINMENT',
                'priority': 'CRITICAL',
                'reporter': user2,
                'assigned_to': manager,
            },
            {
                'title': 'Printer Jam - 2nd Floor',
                'description': 'Main printer is showing error code 50.1.',
                'ticket_type': 'HELPDESK',
                'nist_stage': 'RECOVERY',
                'priority': 'LOW',
                'reporter': user1,
                'assigned_to': tech,
            },
            {
                'title': 'Unauthorized Access Attempt detected on Firewall',
                'description': 'Repeated failed login attempts from a known malicious IP address range.',
                'ticket_type': 'INCIDENT',
                'nist_stage': 'DETECTION',
                'priority': 'MEDIUM',
                'reporter': analyst,
                'assigned_to': analyst,
            },
            {
                'title': 'Laptop Screen Replacement',
                'description': 'Dell XPS screen is flickering and showing lines.',
                'ticket_type': 'HELPDESK',
                'nist_stage': 'PREPARATION',
                'priority': 'MEDIUM',
                'reporter': user2,
                'assigned_to': None,
            },
        ]

        self.stdout.write("Creating tickets and audit logs...")
        for data in tickets_data:
            ticket = Ticket.objects.create(**data)
            
            # Create some dummy updates for audit trail
            if ticket.nist_stage != 'PREPARATION':
                TicketUpdate.objects.create(
                    ticket=ticket,
                    author=random.choice(staff),
                    comment=f"Initial investigation started. Moving to {ticket.nist_stage} stage.",
                    new_stage=ticket.nist_stage
                )
        
        self.stdout.write(self.style.SUCCESS("Successfully populated dummy data!"))
        self.stdout.write(f"Users created: manager1, tech1, analyst1, user1, user2 (Password: password123)")
