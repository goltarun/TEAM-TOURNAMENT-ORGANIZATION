import os
import django
import subprocess
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ff_squad_admin.settings')
django.setup()

from django.core.management import execute_from_command_line

# Start development server in background
try:
    print("Starting Django development server...")
    print("Server will be available at: http://127.0.0.1:8001")
    print("Admin panel: http://127.0.0.1:8001/admin/")
    print("Login: admin / admin123")
    print("\nPress Ctrl+C to stop the server")
    
    # Run server
    sys.argv = ['manage.py', 'runserver', '8001']
    execute_from_command_line(sys.argv)
    
except KeyboardInterrupt:
    print("\nServer stopped by user")
except Exception as e:
    print(f"Error starting server: {e}")
