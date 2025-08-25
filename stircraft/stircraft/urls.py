"""
URL configuration for stircraft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, Http404
from django.views.static import serve
import os

def serve_media(request, path):
    """Custom media serving view for production"""
    media_root = settings.MEDIA_ROOT
    file_path = os.path.join(media_root, path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return serve(request, path, document_root=media_root)
    else:
        raise Http404("Media file not found")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stir_craft.urls')),
    # Custom media serving for production
    path('media/<path:path>', serve_media, name='serve_media'),
]

# Custom error handlers
handler403 = 'stir_craft.views.handler_403'
handler404 = 'stir_craft.views.handler_404'
handler500 = 'stir_craft.views.handler_500'
