from depov3.wsgi import application

# Vercel'in beklediği fonksiyon
def handler(request, **kwargs):
    return application(request, **kwargs) 