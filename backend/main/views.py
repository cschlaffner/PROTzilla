from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie


# API to write csrf token into cookies via decorator
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"message": "CSRF cookie set."})
