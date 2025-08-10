from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import *

urlpatterns = [
    path('', Home.as_view(), name="home"),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'