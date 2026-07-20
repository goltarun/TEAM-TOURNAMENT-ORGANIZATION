import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ff_squad_admin.settings')
django.setup()

from django.core.management import execute_from_command_line
import sys

# Start development server
project_root = os.path.dirname(os.path.abspath(__file__))
manage_py_path = os.path.join(project_root, 'manage.py')
# Ensure the script path exists so Django's autoreloader can re-spawn correctly
sys.argv = [manage_py_path, 'runserver', '8001']
execute_from_command_line(sys.argv)

