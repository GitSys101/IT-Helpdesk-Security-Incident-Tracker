import os

base_dir = r"c:\Users\huawe\OneDrive\ドキュメント\3rd Year\2nd Sem\Integ\Final Project\IT Helpdesk & Security Incident Tracker"

# 1. Restore accounts/models.py
models_path = os.path.join(base_dir, r'accounts\models.py')
with open(models_path, 'r', encoding='utf-8') as f:
    models_content = f.read()

models_content = models_content.replace(
    "('MANAGER', 'IT Manager'),\n        ('USER', 'End User'),",
    "('MANAGER', 'IT Manager'),\n        ('TECHNICIAN', 'IT Technician'),\n        ('ANALYST', 'Security Analyst'),\n        ('USER', 'End User'),"
)

if 'def is_technician(self):' not in models_content:
    models_content += "\n    @property\n    def is_technician(self):\n        return self.role in ['TECHNICIAN', 'ANALYST', 'MANAGER']\n"

with open(models_path, 'w', encoding='utf-8') as f:
    f.write(models_content)

# 2. Restore other files
files_to_restore = [
    r'tickets\views_api.py',
    r'tickets\serializers.py',
    r'templates\base.html'
]

for f in files_to_restore:
    path = os.path.join(base_dir, f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace("is_manager", "is_technician")
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)

# 3. Restore views.py manually
views_path = os.path.join(base_dir, r'tickets\views.py')
with open(views_path, 'r', encoding='utf-8') as file:
    views_content = file.read()

if "def is_technician(user):" not in views_content:
    views_content = views_content.replace(
        "def is_manager(user):\n    return user.is_authenticated and user.role == 'MANAGER'\n",
        "def is_manager(user):\n    return user.is_authenticated and user.role == 'MANAGER'\n\ndef is_technician(user):\n    return user.is_authenticated and (user.role in ['TECHNICIAN', 'ANALYST', 'MANAGER'])\n"
    )

views_content = views_content.replace("if is_manager(user):\n            qs = Ticket.objects.all()", "if is_technician(user):\n            qs = Ticket.objects.all()")
views_content = views_content.replace("elif not is_manager(user):\n            queryset = queryset.filter(reporter=user)", "elif not is_technician(user):\n            queryset = queryset.filter(reporter=user)")
views_content = views_content.replace("if is_manager(user):\n            return Ticket.objects.all()", "if is_technician(user):\n            return Ticket.objects.all()")
views_content = views_content.replace("return is_manager(self.request.user)", "return is_technician(self.request.user)")
views_content = views_content.replace("if is_manager(user) or user.is_staff:\n                    logs = all_logs", "if is_technician(user) or user.is_staff:\n                    logs = all_logs")

with open(views_path, 'w', encoding='utf-8') as file:
    file.write(views_content)

print("Restoration complete.")
