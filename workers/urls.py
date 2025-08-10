from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CambiarEstadoView, AceptarOrdenView, CompletarOrdenView, CancelarOrdenView, WorkerDashboardView, WorkerProfileEditView, WorkerProfileView

urlpatterns = [
    path('', WorkerDashboardView.as_view(), name='worker_dashboard'),
    path('cambiar_estado/', CambiarEstadoView.as_view(), name='cambiar_estado'),
    path('aceptar_orden/<int:reserva_id>/', AceptarOrdenView.as_view(), name='aceptar_orden'),
    path('completar_orden/<int:reserva_id>/', CompletarOrdenView.as_view(), name='completar_orden'),
    path('cancelar_orden/<int:reserva_id>/', CancelarOrdenView.as_view(), name='cancelar_orden'),
    path('perfil/', WorkerProfileView.as_view(), name='worker_profile'),  # URL para ver el perfil
    path('perfil/editar/', WorkerProfileEditView.as_view(), name='worker_profile_edit')
]