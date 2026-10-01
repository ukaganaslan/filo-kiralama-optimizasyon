from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Render health check'i için uygulama ve veritabanı erişimini doğrular."""
    try:
        connection.ensure_connection()
    except Exception:
        return JsonResponse({'status': 'unhealthy'}, status=503)
    return JsonResponse({'status': 'ok'})
