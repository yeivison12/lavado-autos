import csv
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, DetailView, CreateView
from bills.models import Tarifa
from orders.models import Reserva,HorarioDisponible
from orders.signals import EmailSendingError
from .forms import CrearTarifaForm, ReservaForm,HorarioDisponibleForm,ReservaFormUpdate
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from orders.utils import procesar_reserva
from django.contrib.auth import logout
from django.db.models import Q
from django.db import models
from datetime import datetime
from django.utils.translation import gettext as _
from workers.models import Worker
from .validators import validate_month, validate_day, validate_state, validate_date_format
from PIL import Image, ImageDraw, ImageFont
import io

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'administration/lista.html'
    context_object_name = 'object_list'
    ordering = ['-fecha_creacion']
    paginate_by = 10

    def get_queryset(self):
        queryset = Reserva.objects.all().order_by(*self.ordering)
        query = self.request.GET.get('q')
        estado = self.request.GET.get('estado')

        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) |
                Q(telefono__icontains=query) |
                Q(estado__icontains=query)
            )

        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['estado'] = self.request.GET.get('estado', '')
        return context
class ReservaUpdateView(LoginRequiredMixin,AdminRequiredMixin, UpdateView):
    model = Reserva
    form_class = ReservaFormUpdate  
    template_name = 'administration/reserva_from.html'  
    context_object_name = 'reserva'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reserva = self.get_object()
        self.nombre = reserva.nombre  # Almacena el nombre en un atributo de la instancia
        horario_id = reserva.horario.id if reserva.horario else None
        context['horario_id'] = horario_id
        context['nombre'] = self.nombre
        return context 

    def get_success_url(self):
        return reverse_lazy('listaAdmon')

    def get_error_url(self):
        return reverse_lazy('listaAdmon') + '?error'

    def form_valid(self, form):
        try:
            return procesar_reserva(form, self.request, self.get_success_url(), self.get_error_url(), self.template_name)
        except EmailSendingError:
            messages.error(self.request, "No se pudo enviar el correo de confirmación. No se guardaron los cambios.")
            return redirect(self.get_error_url())



class ReservaDeleteView(LoginRequiredMixin,AdminRequiredMixin,DeleteView):
    model = Reserva
    template_name = 'administration/reserva_confirm_delete.html'  
    def get_success_url(self):
        return reverse_lazy('listaAdmon') + '?deleted'
    
class ReservaDetailView(LoginRequiredMixin,AdminRequiredMixin,DetailView):
    model = Reserva
    context_object_name = 'horario'
    template_name = 'administration/reserva_detail.html'  # Template para mostrar los detalles
    context_object_name = 'reserva'
    def get_object(self, queryset=None):
        token = self.kwargs.get('token')
        return get_object_or_404(Reserva, token=token)
class ReservaCreateView(LoginRequiredMixin,AdminRequiredMixin,CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'administration/reserva_create_form.html'
    def get_error_url(self):
        return reverse_lazy('listaAdmon') + '?createerror'
    
    def get_success_url(self):
        return reverse_lazy('listaAdmon') + '?updated'
    
    def form_valid(self, form):
        request = self.request
        success_url = self.get_success_url()
        error_url = self.get_error_url()
        template_name = self.template_name
        return procesar_reserva(form, request, success_url,error_url, template_name)
    
# Vista para crear un nuevo horario disponible
class CrearHorarioView(LoginRequiredMixin,SuccessMessageMixin,AdminRequiredMixin, CreateView):
    model = HorarioDisponible
    form_class = HorarioDisponibleForm
    template_name = 'administration/crear_horarios.html'
    success_url = reverse_lazy('listar_horarios')
    success_message = "Horario creado exitosamente."
#crea una tarifa
class CrearTarifaView(LoginRequiredMixin, SuccessMessageMixin, AdminRequiredMixin, CreateView):
    model = Tarifa
    form_class = CrearTarifaForm
    template_name = 'administration/crear_tarifa.html'
    success_url = reverse_lazy('listar_tarifas')
    success_message = "Tarifa creada exitosamente."

class ListarTarrifas(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Tarifa
    template_name = 'administration/listar_tarifas.html'
    context_object_name = 'tarifas'
    ordering = ['-fecha_creacion']
    paginate_by = 10

    def get_queryset(self):
        queryset = Tarifa.objects.all().order_by(*self.ordering)
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(Q(nombre__icontains=query))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
class EditarTarifaView(UpdateView):
    model = Tarifa
    form_class = CrearTarifaForm
    template_name = 'administration/editar_tarifa.html'
    success_url = reverse_lazy('listar_tarifas')

class EliminarTarifaView(DeleteView):
    model = Tarifa
    template_name = 'administration/eliminar_tarifa.html'
    success_url = reverse_lazy('listar_tarifas')

# Vista para actualizar un horario existente
class ActualizarHorarioView(LoginRequiredMixin,SuccessMessageMixin,AdminRequiredMixin, UpdateView):
    model = HorarioDisponible
    form_class = HorarioDisponibleForm
    template_name = 'administration/actualizar_horarios.html'
    success_message = "Horario actualizado exitosamente."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        horario = self.get_object()
        reservas = horario.reservas.all()  # Usa el related_name definido en el modelo Reserva
        # Agregar las reservas al contexto
        context['reservas'] = reservas
        # Si quieres mostrar solo el nombre de la última reserva
        ultima_reserva = reservas.last()
        if ultima_reserva:
            context['nombre_persona'] = ultima_reserva.nombre
        else:
            context['nombre_persona'] = None  # No hay reservas asociadas
        return context
    def get_success_url(self):
            return reverse_lazy('listaAdmon') + '?dateupdated' 
    def get_error_url(self):
        return reverse_lazy('listaAdmon') + '?error'

class ListarHorariosView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = HorarioDisponible
    template_name = 'administration/listar_horarios.html'
    context_object_name = 'horarios'
    ordering = ['fecha', 'hora']
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')

        if query:
            # Validar mes
            month_number = validate_month(query)
            if month_number:
                queryset = queryset.filter(fecha__month=month_number)

            # Validar día
            day_number = validate_day(query)
            if day_number:
                queryset = queryset.filter(fecha__day=day_number)

            # Validar estado
            estado = validate_state(query)
            if estado is not None:
                queryset = queryset.filter(disponible=estado)

            # Validar fecha en formato 'día mes'
            date_parts = validate_date_format(query)
            if date_parts:
                day, month = date_parts
                queryset = queryset.filter(fecha__day=day, fecha__month=month)

        return queryset
class WorkerListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Worker
    template_name = 'administration/lista_trabajadores.html'
    context_object_name = 'trabajadores'
    ordering = ['user']  # Ajusta según el campo de nombre en tu modelo
    paginate_by = 10


    def get_queryset(self):
        queryset = Worker.objects.all().select_related('user')
        q = self.request.GET.get('q', '').strip()
        estado = self.request.GET.get('estado', '').strip().lower()

        if q:
            queryset = queryset.filter(
                models.Q(user__first_name__icontains=q) |
                models.Q(user__last_name__icontains=q) |
                models.Q(user__email__icontains=q)
            )
        if estado and estado in dict(Worker.ESTADOS):
            queryset = queryset.filter(estado=estado)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Usa el queryset completo para los totales, NO el paginado
        full_queryset = self.get_queryset()
        context['conectados'] = full_queryset.filter(estado='conectado').count()
        context['ocupados'] = full_queryset.filter(estado='ocupado').count()
        context['ausentes'] = full_queryset.filter(estado='ausente').count()
        context['q'] = self.request.GET.get('q', '')
        context['estado'] = self.request.GET.get('estado', '')
        return context

class CustomLoginView(LoginView):
    template_name = 'administration/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse_lazy('listaAdmon') + '?login'
        if user.groups.filter(name='Trabajadores').exists():
            return reverse_lazy('worker_dashboard') + '?login'
        return reverse_lazy('home') + '?login'
    
def custom_logout(request):
    if request.user.groups.filter(name='Trabajadores').exists():
        try:
            worker = request.user.worker
            if worker.servicio_actual:
                messages.error(request, 'No puedes cerrar sesión hasta que completes el servicio actual.')
                return redirect('worker_dashboard')
        except Worker.DoesNotExist:
            messages.error(request, 'No tienes un perfil de trabajador asociado.')
            return redirect('home')
    
    logout(request)
    return redirect('/?logout')



from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def exportar_trabajadores_imagen(request):
    from django.utils import timezone

    # Cargar datos
    trabajadores = Worker.objects.select_related('user').all()
    filas = [["Nombre", "Correo", "Estado", "Fecha de Creacion"]]
    for w in trabajadores:
        fecha_creacion = w.user.date_joined.strftime("%d/%m/%Y %H:%M") if hasattr(w.user, "date_joined") else "-"
        filas.append([
            f"{w.user} {w.user.last_name}",
            w.user.email if w.user.email else "No disponible",
            w.get_estado_display(),
            fecha_creacion
        ])

    # Encabezado de la app y fecha de exportación
    nombre_app = "Lavado de Autos"
    fecha_export = timezone.now().strftime("%d/%m/%Y %H:%M")
    encabezado = f"{nombre_app} - Exportacion de Trabajadores"
    sub_encabezado = f"Fecha de exportacion: {fecha_export}"

    # Estilos
    fuente = ImageFont.load_default()
    ancho_col = [max(len(str(cell)) for cell in col) * 10 for col in zip(*filas)]
    alto_fila = 25
    padding = 10

    # Calcular ancho de encabezados
    ancho_encabezado = max(fuente.getlength(encabezado), fuente.getlength(sub_encabezado))
    ancho_tabla = sum(ancho_col)
    ancho_img = max(ancho_tabla, int(ancho_encabezado)) + padding * 2
    alto_img = (len(filas) + 3) * alto_fila + padding * 2  # +3 para encabezados

    # Crear imagen
    img = Image.new("RGB", (ancho_img, alto_img), "white")
    draw = ImageDraw.Draw(img)

    # Dibujar encabezados
    y = padding
    draw.text((padding, y), encabezado, fill="black", font=fuente)
    y += alto_fila
    draw.text((padding, y), sub_encabezado, fill="black", font=fuente)
    y += alto_fila

    # Dibujar tabla
    for fila in filas:
        x = padding
        for i, celda in enumerate(fila):
            draw.text((x, y), str(celda), fill="black", font=fuente)
            x += ancho_col[i]
        y += alto_fila

    # Guardar en memoria
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")