"""noob URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from apps import improductivos
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # Renderiza al index de improductivos
    path('', include('apps.improductivos.urls', namespace="improductivos")),
    path('usuario/', include('apps.usuario.urls', namespace='usuario')),
    path('producciones/', include('apps.producciones.urls', namespace='producciones')),
    # path('sync_google_sheet/',include('apps.sync_google_sheet.urls',namespace='sync_google_sheet')),

]

# if settings.DEBUG:
#    urlpatterns += static(settings.STATIC_URL,
#                          document_root=settings.STATIC_ROOT)
#handler404 = improductivos.views.handler404
#handler500 = improductivos.views.handler500
