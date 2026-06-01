import os

base_dir = r"c:\Users\huawe\OneDrive\ドキュメント\3rd Year\2nd Sem\Integ\Final Project\IT Helpdesk & Security Incident Tracker"
files_to_replace = [
    r'tickets\views.py',
    r'tickets\views_api.py',
    r'tickets\serializers.py',
    r'templates\base.html'
]

for f in files_to_replace:
    path = os.path.join(base_dir, f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if f == r'tickets\views.py':
        to_remove = "def is_technician(user):\n    return user.is_authenticated and (user.role in ['TECHNICIAN', 'ANALYST', 'MANAGER'])\n"
        content = content.replace(to_remove, "")
    
    content = content.replace("is_technician", "is_manager")
    
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)

print("Replacement complete.")
