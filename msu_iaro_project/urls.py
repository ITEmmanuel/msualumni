"""
URL Configuration for msu_iaro_project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('alumni/', include('alumni.urls')),
    path('admin-portal/', include('admin_portal.urls')),
    # Root URL directs to alumni app but needs a unique namespace to avoid duplication
    path('', include(('alumni.urls', 'alumni'), namespace='alumni_root')),  # unique namespace
    # Redirect default auth profile page to admin portal dashboard
    path('accounts/profile/', RedirectView.as_view(pattern_name='admin_portal:dashboard', permanent=False)),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)