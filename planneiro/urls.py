from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # ✅ Agregar
from django.conf.urls.static import static  # ✅ Agregar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('applogin.urls')),
]

# ✅ Agregar esto al final para servir archivos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)