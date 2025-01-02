from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from invitations.views import accept_invitation


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.home.urls')),
    path('', include('apps.accounts.urls')),
    path('', include('apps.dashboard.urls')),

    path("invitations/", include('invitations.urls', namespace='invitations')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
