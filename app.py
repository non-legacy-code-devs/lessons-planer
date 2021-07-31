"""
WSGI config for myapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import sys

this_file = "www/venv/bin/activate_this.py"
exec(open(this_file).read(), {'__file__': this_file})

# add your project directory to the sys.path
project_home = u'/home/nujgoiz/myapp'
if project_home not in sys.path:
    sys.path.append(project_home)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')

application = get_wsgi_application()