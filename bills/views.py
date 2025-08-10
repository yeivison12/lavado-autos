from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from car_wash.settings import EMAIL_HOST_USER
from .models import Recibo
from orders.models import Reserva
from .forms import ReciboForm
from django.core.mail import EmailMessage
from django.views.generic import UpdateView
from django.contrib import messages

from xhtml2pdf import pisa


class GenerarReciboView(LoginRequiredMixin, CreateView):
    model = Recibo
    form_class = ReciboForm
    template_name = 'bills/generar_recibo.html'

    def dispatch(self, request, *args, **kwargs):
        """ Verifica que el usuario sea el trabajador asignado a la reserva. """
        reserva = get_object_or_404(Reserva, id=self.kwargs['reserva_id'])

        # Si ya existe un recibo para esta reserva, redirige a su detalle
        if hasattr(reserva, 'recibo'):
            return redirect('ver_recibo', pk=reserva.recibo.id)

        if reserva.trabajador is None or reserva.trabajador.user != request.user:
            return redirect('error_permiso')  # Redirigir si no es el trabajador asignado

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        reserva = get_object_or_404(Reserva, id=self.kwargs['reserva_id'])
        recibo = form.save(commit=False)
        recibo.reserva = reserva
        recibo.trabajador = reserva.trabajador

        if not recibo.monto:
            recibo.monto = reserva.servicio.monto 
        recibo.save()
        return redirect('ver_recibo', pk=recibo.id)

    def get_context_data(self, **kwargs):
        """ Agrega la reserva al contexto para mostrar detalles en el template. """
        context = super().get_context_data(**kwargs)
        context['reserva'] = get_object_or_404(Reserva, id=self.kwargs['reserva_id'])
        return context


class ReciboDetailView(LoginRequiredMixin, DetailView):
    model = Recibo
    template_name = 'bills/recibo.html'
    context_object_name = 'recibo'

    def dispatch(self, request, *args, **kwargs):
        recibo = self.get_object()
        if recibo.trabajador.user != request.user:
            return redirect('error_permiso')
        return super().dispatch(request, *args, **kwargs)

class ActualizarReciboView(LoginRequiredMixin, UpdateView):
    model = Recibo
    form_class = ReciboForm
    template_name = 'bills/actualizar_recibo.html'
    context_object_name = 'recibo'

    def dispatch(self, request, *args, **kwargs):
        recibo = self.get_object()
        if recibo.trabajador.user != request.user:
            return redirect('error_permiso')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('ver_recibo', kwargs={'pk': self.object.pk})

def generar_pdf(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        recibo = get_object_or_404(Recibo, pk=pk)

        if recibo.trabajador.user != request.user:
            return redirect('error_permiso')

        # Renderizar HTML como PDF
        template_path = 'bills/recibo.html'
        context = {'recibo': recibo, 'is_pdf': True}
        html = render_to_string(template_path, context)
        response = BytesIO()
        pdf = pisa.CreatePDF(src=html, dest=response, encoding='UTF-8')

        if not pdf.err:
            try:
                email = EmailMessage(
                    subject='Tu recibo',
                    body='Adjunto encontrarás tu recibo en formato PDF.',
                    from_email=EMAIL_HOST_USER,
                    to=[recibo.reserva.email],
                )
                email.attach(
                    filename=f'recibo_{recibo.id}.pdf',
                    content=response.getvalue(),
                    mimetype='application/pdf'
                )
                email.send()

                messages.success(request, 'Correo enviado exitosamente con el PDF adjunto.')
            except Exception as e:
                messages.error(request, f'Error al enviar el correo: {str(e)}')
        else:
            messages.error(request, 'Error al generar el PDF.')

        return redirect(reverse_lazy('ver_recibo', kwargs={'pk': recibo.id}))
    else:
        return HttpResponse('Método no permitido', status=405)
    
def error_permiso(request):
    return render(request, 'bills/error_permiso.html', status=403)