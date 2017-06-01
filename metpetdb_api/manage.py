#!/usr/bin/env python
import os
import sys
import dotenv
from getenv import env


if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(__file__)
    sys.path.insert(-1, os.path.join(PROJECT_ROOT, "vendor/djoser"))
	
    dotenv.read_dotenv('api.env')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", env('API_SETTINGS'))

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
