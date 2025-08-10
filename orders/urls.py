
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from .views import ReservarView


urlpatterns = [
    path('reserva',ReservarView.as_view(), name='reservation'),
]