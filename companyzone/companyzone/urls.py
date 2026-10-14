"""
URL configuration for companyzone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from accounts import views as acc_views
from django.views.generic import TemplateView


urlpatterns = [
    # AVOID THIS IN PRODUCTION:
    # path('admin/', admin.site.urls),
    # PRODUCTION PRACTICE: Use a secure, secret custom path string - environment variable
    path(settings.ADMIN_PATH, admin.site.urls), 
    
    path('emp/', include('empapp.urls')),
    path('accounts/', include('accounts.urls')),

    # Your app's landing page
    path('', acc_views.dashboard),
    path('dashboard/', acc_views.dashboard, name='dashboard_url'),

    path('3dmodeltest/', TemplateView.as_view(template_name='3d_model_view.html'), name='3dmodeltest_url'),

    path('api/', include('api.urls'))
]


if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar

    # To make Debug toolbar only works on DEBUG=True
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls))
    ]

    # Standard Media Setup:
    # static() helper function is programmed to only work when DEBUG=True. 
    # The moment you flip DEBUG = False to run your production test, the static() helper completely turns off and returns nothing.
    # Serves user uploaded media files locally on your laptop
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)


# FORCED TEMPORARY MEDIA SERVING ON PRODUCTION (even if DEBUG = False/True)
# -------------------------------------------------------------------------
# if settings.MEDIA_URL and settings.MEDIA_ROOT:
#     # serve view
#     from django.views.static import serve
#     from django.urls import re_path

#     urlpatterns += [
#         re_path(r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'), serve, {
#             'document_root': settings.MEDIA_ROOT,
#         }),
#     ]

# by default, Django's built-in static() function refuses to serve media files 
# when DEBUG = False (production mode).
# so even if you use "urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)"
# in production iut will not serves files

# Django is intentionally built that way because it is a Python web framework, 
# not a high-speed file storage server. In a corporate environment, 
# letting Django process raw media files can clog the system and slow down performance.