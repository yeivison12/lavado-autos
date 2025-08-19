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

        # Solo tarifas activas
        servicios_activos = Tarifa.objects.filter(activo=True)

        # Diccionario de precios
        context['precios'] = {
            unicodedata.normalize('NFKD', t.nombre).encode('ascii', 'ignore').decode().lower().replace(' ', '_'): t.monto
            for t in servicios_activos
        }

        # Servicios
        context['primeros_tres'] = servicios_activos[:3]
        context['restantes'] = servicios_activos[3:] if servicios_activos.count() > 3 else []

        return context

    
def handler404(request, exception):
        return render(request, 'core/404.html', status=404)

def handler500(request):
        return render(request, 'core/500.html', status=500)
