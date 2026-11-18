import os
import sys

# Ensure smart_farming_dss directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(root_dir, 'smart_farming_dss')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import app

# Vercel entrypoint
app = app
