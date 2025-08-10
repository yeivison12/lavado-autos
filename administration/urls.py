from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    CrearTarifaView,
    EditarTarifaView,
    EliminarTarifaView,
    ListarTarrifas,
    ReservaListView,
    ReservaCreateView,
    ReservaUpdateView,
    ReservaDetailView,
    ReservaDeleteView,
    CrearHorarioView,
    ActualizarHorarioView,
    ListarHorariosView,
    CustomLoginView,
    WorkerListView,
    custom_logout,
    exportar_trabajadores_imagen
)


urlpatterns = [
    path('', ReservaListView.as_view(), name='listaAdmon'),
    path('nueva/', ReservaCreateView.as_view(), name='reserva_create'),
    path('<int:pk>/editar/', ReservaUpdateView.as_view(), name='reserva_edit'),
    path('<int:pk>/', ReservaDetailView.as_view(), name='reserva_detail'),
    
    
    path('<int:pk>/eliminar/', ReservaDeleteView.as_view(), name='reserva_delete'),
    path('listar/', ListarHorariosView.as_view(), name='listar_horarios'),
    path('crear/', CrearHorarioView.as_view(), name='crear_horario'),
    path('tarifas/', ListarTarrifas.as_view(), name='listar_tarifas'),
    path('tarifas/crear/', CrearTarifaView.as_view(), name='crear_tarifa'),
    path('tarifas/<int:pk>/editar/', EditarTarifaView.as_view(), name='editar_tarifa'),
    path('tarifas/<int:pk>/eliminar/', EliminarTarifaView.as_view(), name='eliminar_tarifa'),
    path('actualizar/<int:pk>/', ActualizarHorarioView.as_view(), name='actualizar_horario'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', custom_logout, name='logout'),
    path('trabajadores/', WorkerListView.as_view(), name='lista_trabajadores'),
    path('trabajadores/exportar/', exportar_trabajadores_imagen, name='exportar_trabajadores'),

]