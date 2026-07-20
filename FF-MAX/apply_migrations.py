import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ff_squad_admin.settings')
django.setup()

from django.core.management import execute_from_command_line
import sys

# Apply migrations
sys.argv = ['manage.py', 'migrate']
execute_from_command_line(sys.argv)
