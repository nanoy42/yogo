"""
WSGI config for yogo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import sys

VIRTUALENV_LOC = '/var/www/yogo/env_yogo'

activate_env=os.path.join(VIRTUALENV_LOC, 'bin/activate_this.py')
exec(compile(open(activate_env, "rb").read(), activate_env, 'exec'), {'__file__':activate_env})
sys.path.append('/var/www/yogo')
sys.path.append('/var/www/yogo/yogo')


from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yogo.settings")
application = get_wsgi_application()
