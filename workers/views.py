from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib import messages
from django.apps import apps
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from .models import Worker
from .forms import WorkerForm
from django.core.mail import send_mail
from django.conf import settings
from orders.signals import EmailSendingError
class WorkerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Trabajadores').exists()
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permiso para acceder a esta página.')
        return redirect('home')
class CambiarEstadoView(LoginRequiredMixin, WorkerRequiredMixin, View):
    def post(self, request):
        estado = request.POST.get('estado')
        worker = request.user.worker
        try:
            if estado == 'hora de comida':
                worker.cambiar_estado('hora de comida')
                messages.success(request, 'Estado cambiado a Hora de Comida')
            elif estado == 'conectado' and worker.estado == 'hora de comida':
                worker.cambiar_estado('conectado')
                messages.success(request, 'Estado cambiado a Conectado')
            else:
                messages.error(request, 'Estado no permitido')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('worker_dashboard')
    
class AceptarOrdenView(LoginRequiredMixin, WorkerRequiredMixin, View):
    def post(self, request, reserva_id):
        worker = request.user.worker
        Reserva = apps.get_model('orders', 'Reserva')
        reserva = get_object_or_404(Reserva, id=reserva_id)

        if worker.estado != 'conectado':
            messages.error(request, 'No puedes aceptar órdenes mientras no estés disponible.')
            return redirect('worker_dashboard')

        if reserva.trabajador is not None:
            messages.error(request, 'Esta orden ya fue aceptada por otro trabajador.')
            return redirect('worker_dashboard')

        try:
            with transaction.atomic():
                reserva.trabajador = worker
                reserva.estado = 'confirmado'
                reserva.save()  # Esto lanza EmailSendingError si falla

                worker.servicio_actual = reserva
                worker.cambiar_estado('ocupado')

            messages.success(request, 'Orden aceptada exitosamente. Se notificó al cliente.')

        except EmailSendingError as e:
            transaction.set_rollback(True)
            print(f"[ERROR] {e}")
            messages.error(request, 'No se pudo enviar el correo al cliente. La orden no fue aceptada.')
            return redirect('worker_dashboard')

        except Exception as e:
            print(f"[ERROR] Error general al aceptar orden: {e}")
            messages.error(request, 'Ocurrió un error. Intenta nuevamente.')
            return redirect('worker_dashboard')

        return redirect('worker_dashboard')

class CompletarOrdenView(LoginRequiredMixin, WorkerRequiredMixin, View):
    def post(self, request, reserva_id):
        worker = request.user.worker
        Reserva = apps.get_model('orders', 'Reserva')
        reserva = get_object_or_404(Reserva, id=reserva_id)

        if worker.servicio_actual != reserva:
            messages.error(request, 'No puedes completar esta orden.')
            return redirect('worker_dashboard')

        try:
            with transaction.atomic():
                reserva.estado = 'completado'
                reserva.save()

                worker.servicio_actual = None
                worker.cambiar_estado('conectado')

            messages.success(request, 'Orden completada exitosamente. Se notificó al cliente.')
        except Exception as e:
            print(f"[ERROR] Error al completar orden: {e}")
            messages.error(request, 'No se pudo completar la orden. Intenta nuevamente.')

        return redirect('worker_dashboard')

class CancelarOrdenView(LoginRequiredMixin, WorkerRequiredMixin, View):
    def post(self, request, reserva_id):
        worker = request.user.worker
        Reserva = apps.get_model('orders', 'Reserva')
        reserva = get_object_or_404(Reserva, id=reserva_id)

        if worker.servicio_actual != reserva:
            messages.error(request, 'No puedes cancelar esta orden.')
            return redirect('worker_dashboard')

        try:
            with transaction.atomic():
                reserva.estado = 'pendiente'
                reserva.trabajador = None
                reserva.save()

                worker.servicio_actual = None
                worker.cambiar_estado('conectado')

            messages.success(request, 'Orden cancelada exitosamente. Se notificó al cliente.')
        except Exception as e:
            print(f"[ERROR] Error al cancelar orden: {e}")
            messages.error(request, 'No se pudo cancelar la orden. Intenta nuevamente.')

        return redirect('worker_dashboard')



class WorkerDashboardView(LoginRequiredMixin, WorkerRequiredMixin, View):
    def get(self, request):
        try:
            worker = request.user.worker
        except Worker.DoesNotExist:
            messages.error(request, 'No tienes un perfil de trabajador asociado.')
            return redirect('home')  

        Reserva = apps.get_model('orders', 'Reserva')
        reservas_pendientes = Reserva.objects.filter(estado='confirmado')
        
        # Búsqueda en órdenes completadas
        query = request.GET.get('q')
        if query:
            reservas_completadas = Reserva.objects.filter(
                Q(estado='completado') & Q(trabajador=worker) & 
                (Q(nombre__icontains=query) | Q(horario__fecha__icontains=query) | Q(token__icontains=query))
            )
        else:
            reservas_completadas = Reserva.objects.filter(estado='completado', trabajador=worker)
        
        # Paginación para órdenes completadas
        paginator = Paginator(reservas_completadas, 5)  # 5 órdenes por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'workers/dashboard.html', {
            'worker': worker,
            'reservas_pendientes': reservas_pendientes,
            'page_obj': page_obj,
            'reserva_actual': worker.servicio_actual,
            'query': query
        })


class WorkerProfileView(LoginRequiredMixin, WorkerRequiredMixin, ListView):
    model = Worker
    template_name = 'workers/profile.html'
    context_object_name = 'reservas' 
    paginate_by = 5 

    def get_queryset(self):
        # Obtener las reservas del trabajador actual
        return self.request.user.worker.reservas.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar el perfil del trabajador al contexto
        context['worker'] = self.request.user.worker
        return context

class WorkerProfileEditView(LoginRequiredMixin, WorkerRequiredMixin, UpdateView):
    model = Worker
    form_class = WorkerForm
    
    template_name = 'workers/profile_edit.html'
    success_url = reverse_lazy('worker_profile')

    def get_object(self, queryset=None):
        return Worker.objects.filter(user=self.request.user).first()
