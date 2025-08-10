from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView
from orders.models import Reserva

class ReservationDetailView(TemplateView):
    template_name = 'reservations/reservation_detail.html'  

    def get(self, request, *args, **kwargs):
        uid = request.GET.get('uid')
        if not uid:
            return render(request, 'reservations/error.html', {'error': 'UID es requerido para acceder a esta página.'})
        
        try:
            reserva = get_object_or_404(Reserva, token=uid)
            return render(request, self.template_name, {'reserva': reserva})
        
        except Reserva.DoesNotExist:
            error_message = 'Reservation not found'
            return self.handle_error(request, error_message, 404)
        except Exception as e:
            return self.handle_error(request, str(e), 500)

    def handle_error(self, request, error_message, status_code):
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({'error': error_message}, status=status_code)
        return render(request, self.template_name, {'error': error_message}, status=status_code)

#Esta vista permite buscar una reserva por su UID y redirigir a la página de estado de la reserva. 
#Estado-reserva 
class ReservationDetailInput(TemplateView):
    template_name = 'reservations/searchorderbyuid.html'

    def get(self, request, *args, **kwargs):
        uid = request.GET.get('uid')
        if uid:
            try:
                Reserva.objects.get(token=uid)
                return redirect(f"{reverse('estado')}?uid={uid}")
            except Reserva.DoesNotExist:
                context = {'error': 'Reservation not found'}
            except Exception as e:
                context = {'error': str(e)}
        else:
            context = {}
        return render(request, self.template_name, context)