from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve


def healthz(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('healthz/', healthz),
    path('api/complaints/', include('complaints.urls')),   # correct
    path('api/admin/', include('complaints.admin_urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        )
    ]
