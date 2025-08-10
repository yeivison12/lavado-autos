"""
URL configuration for car_wash project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import include, path, re_path
from django.views.static import serve

from django.conf import settings
from django.conf.urls.static import static
from administration.views import ReservaDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pedidos/', include('administration.urls')),
    path('reservations/view/<uuid:token>/', ReservaDetailView.as_view(), name='reserva_detail'),
    path('reservations/', include('reservations.urls')),
    path('orders/', include('orders.urls')),
    path('workers/', include('workers.urls')),
    path('bills/', include('bills.urls')),
    path('', include('core.urls')),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

# esto es para servir archivos estáticos y de medios en modo de producción
# Solo se debe usar en desarrollo, en producción se recomienda usar un servidor web como Nginx o Apache para servir archivos estáticos y de medios.
#Borra esto cuando vayas a producción[Ya que no es seguro dejarlo así, ya que puede exponer archivos sensibles] lo hago por capricho para que cargue el css y js del admin cuando el debug está en false
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
         re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
     ]