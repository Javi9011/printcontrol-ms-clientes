from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "service": "ms-clientes",
        "status": "running",
        "version": "1.0"
    })