
from django.contrib import admin
from django.urls import path, include
from citas.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('secure-admin/', admin.site.urls),
    path('', include('citas.urls'))
]
# Servir archivos estáticos durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)