# in wsgi.py
from werkzeug.middleware.proxy_fix import ProxyFix
from app import app
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
