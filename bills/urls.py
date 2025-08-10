from django.urls import path
from .views import( GenerarReciboView, ReciboDetailView,
                   generar_pdf,ActualizarReciboView, 
                   error_permiso)

urlpatterns = [
    path('generar_recibo/<int:reserva_id>/', GenerarReciboView.as_view(), name='generar_recibo'),
    path('recibo/<int:pk>/', ReciboDetailView.as_view(), name='ver_recibo'),
     path('recibo/<int:pk>/actualizar/', ActualizarReciboView.as_view(), name='actualizar_recibo'),
    path('recibo/<int:pk>/generar_pdf/', generar_pdf, name='generar_pdf'),
     path('error-permiso/', error_permiso, name='error_permiso'),
    
]
