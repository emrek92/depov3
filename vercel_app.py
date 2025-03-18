from depov3.wsgi import app

# Vercel serverless function handler
def handler(request, **kwargs):
    return app(request, **kwargs) 