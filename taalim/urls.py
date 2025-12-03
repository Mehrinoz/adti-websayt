from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Asosiy sayt (bosh sahifa, kitoblar va h.k.)
    path('', include('mainapp.urls')),
    # Test tizimi (yangi `testapp`)
    path('', include('testapp.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


