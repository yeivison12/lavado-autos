from django.urls import path
from .views import *

urlpatterns = [
    path('', ReservationDetailInput.as_view(), name='verificar'),
    path('state/', ReservationDetailView.as_view(), name='estado'),
    
]
