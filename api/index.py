import os
import sys

# Ensure smart_farming_dss directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(root_dir, 'smart_farming_dss')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import app

# WSGI middleware to strip Vercel serverless routing prefix if present
class PrefixFixMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        for prefix in ['/api/index.py', '/api/index', '/api']:
            if path_info == prefix:
                environ['PATH_INFO'] = '/'
                break
            elif path_info.startswith(prefix + '/'):
                environ['PATH_INFO'] = path_info[len(prefix):]
                break
        return self.wsgi_app(environ, start_response)

app.wsgi_app = PrefixFixMiddleware(app.wsgi_app)
