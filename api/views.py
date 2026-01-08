from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def signup(request):
    return JsonResponse({"message": "Signup API working"})

@csrf_exempt
def login(request):
    return JsonResponse({"message": "Login API working"})

@csrf_exempt
def test_api(request):
    return JsonResponse({"message": "Backend running successfully 🚀"})

def home(request):
    return HttpResponse("RRR Shopkart Backend is running 🚀")
