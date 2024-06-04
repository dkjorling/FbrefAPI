import sys
sys.path.append('/var/task/vendor')
from app import app
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi

# Convert WSGI app to ASGI
asgi_app = WsgiToAsgi(app)

def lambda_handler(event, context):
    handler = Mangum(asgi_app)
    return handler(event, context)