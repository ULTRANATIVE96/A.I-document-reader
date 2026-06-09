import sys
import os
import importlib.util

# Add the server directory to the Python path so local imports within server/ main.py resolve correctly
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server')
sys.path.insert(0, server_dir)

# Load server/main.py dynamically under a unique module name ('server_main') to prevent circular import collisions
spec = importlib.util.spec_from_file_location("server_main", os.path.join(server_dir, "main.py"))
server_main = importlib.util.module_from_spec(spec)
sys.modules["server_main"] = server_main
spec.loader.exec_module(server_main)

# Expose 'app' for Gunicorn (main:app)
app = server_main.app
