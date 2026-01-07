from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "Backend is alive ✅"})
