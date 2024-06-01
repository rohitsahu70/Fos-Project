#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

class SettingsModuleNotSetException(Exception):
    def __init__(self, message="DJANGO_SETTINGS_MODULE is not set. Please set it before running the application."):
        self.message = message
        super().__init__(self.message)

        

def main():
    """Run administrative tasks."""

    # Set DJANGO_SETTINGS_MODULE if not already set
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fos_database_server.settings.development')

    # Check if DJANGO_SETTINGS_MODULE is set
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
    if not settings_module:
        raise SettingsModuleNotSetException()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
