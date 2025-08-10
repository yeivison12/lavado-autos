import unicodedata
from django.views.generic import TemplateView
from django.shortcuts import render
from bills.models import Tarifa
import unicodedata
# Create your views here.
class Home(TemplateView):
    template_name = "core/lavadoautos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Tarifa a diccionaria
        context['precios'] = {
            unicodedata.normalize('NFKD', t.nombre).encode('ascii', 'ignore').decode().lower().replace(' ', '_'): t.monto
            for t in Tarifa.objects.all()
        }

        # Servicios
        servicios = Tarifa.objects.all()
        context['primeros_tres'] = servicios[:3]
        context['restantes'] = servicios[3:] if servicios.count() > 3 else []

        return context

    
def handler404(request, exception):
        return render(request, 'core/404.html', status=404)

def handler500(request):
        return render(request, 'core/500.html', status=500)