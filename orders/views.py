from django.views.generic import TemplateView
from django.shortcuts import render
from django.urls import reverse_lazy
from .forms import ReservaForm
from .utils import procesar_reserva

class ReservarView(TemplateView):
    template_name = 'orders/reserva.html'

    def get_success_url(self):
        return reverse_lazy('home') + '?success'

    def get_error_url(self):
        return reverse_lazy('home') + '?error'

    def get(self, request):
        form = ReservaForm()
        return render(request, self.template_name, {'form': form})
 
    def post(self, request):
      form = ReservaForm(request.POST)
      if form.is_valid():
            # Llama a la función procesar_reserva
            success_url = self.get_success_url()
            error_url = self.get_error_url()
            return procesar_reserva(form, request, success_url, error_url, self.template_name)
      else:
            return render(request, self.template_name, {'form': form})