"""
WSGI config for MediLocate AI backend project.
"""

import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
