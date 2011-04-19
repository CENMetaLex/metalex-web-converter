import os
import sys

path = '/var/metalex/metalex-web-converter/src/metalex_web_converter'
if path not in sys.path :
	sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'metalex_web_converter.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()


