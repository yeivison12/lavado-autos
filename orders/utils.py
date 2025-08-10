from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from car_wash import settings
from orders.signals import EmailSendingError
from .models import HorarioDisponible, Reserva

def procesar_reserva(form, request, success_url, error_url, template_name):
    reserva = form.save(commit=False)

    if reserva.estado in ['pendiente', 'confirmado']:
        reserva.trabajador = None

    try:
        with transaction.atomic():
            reserva.save()
            form.save_m2m()

        messages.success(request, f'La reserva de {reserva.nombre} ha sido actualizada exitosamente.')
        return redirect(success_url)

    except Exception as e:
        print(f"[ERROR] Fallo al guardar reserva: {e}")
        messages.error(request, 'No se pudo guardar la reserva. Intenta nuevamente.')
        return redirect(error_url)
