import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ff_squad_admin.settings')
django.setup()

from django.contrib.auth.models import User

# Delete existing admin user and create new one
User.objects.filter(username='admin').delete()
admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print("Admin user created successfully!")
print("Username: admin")
print("Password: admin123")
