from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500


from django.conf import settings
from django.conf.urls.static import static
from main.views import _handler404

urlpatterns = [
    path('', include('main.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# handler404 = 'main.viewss._handler404'