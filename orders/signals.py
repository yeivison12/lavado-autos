from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.exceptions import ValidationError

from car_wash.settings import EMAIL_HOST_USER
from .models import Reserva

class EmailSendingError(Exception):
    """Excepción personalizada para errores al enviar correos."""
    pass

@receiver(pre_save, sender=Reserva)
def capturar_estado_previo(sender, instance, **kwargs):
    """Captura el estado y trabajador previo de una reserva antes de guardar."""
    if instance.pk:
        try:
            reserva_anterior = Reserva.objects.get(pk=instance.pk)
            instance._old_estado = reserva_anterior.estado
            instance._old_trabajador = reserva_anterior.trabajador
        except Reserva.DoesNotExist:
            instance._old_estado = None
            instance._old_trabajador = None
    else:
        instance._old_estado = None
        instance._old_trabajador = None

@receiver(post_save, sender=Reserva)
def enviar_correo_confirmacion(sender, instance, created, **kwargs):
    """Envía correos según el estado o cambios en la reserva."""

    asunto = mensaje = None
    old_estado = getattr(instance, '_old_estado', None)
    new_estado = instance.estado
    old_trabajador = getattr(instance, '_old_trabajador', None)
    new_trabajador = instance.trabajador

    if created:
        asunto = '¡Tu reserva ha sido creada!'
        mensaje = (
            f"Hola {instance.nombre},\n\n"
            f"Tu reserva ha sido creada exitosamente.\n"
            f"- Servicio: {instance.servicio.nombre}\n"
            f"- Precio: {instance.servicio.monto}\n"
            f"- Fecha: {instance.horario.fecha}\n"
            f"- Hora: {instance.horario.hora}\n"
            f"- Código: {instance.token}\n\n"
            f"Gracias por elegirnos."
        )

    else:
        if old_estado != new_estado:
            if new_estado == 'completado':
                asunto = '¡Tu reserva ha sido completada!'
                mensaje = (
                    f"Hola {instance.nombre},\n\n"
                    f"Tu reserva ha sido completada exitosamente.\n"
                    f"- Servicio: {instance.servicio.nombre}\n"
                    f"- Precio: {instance.servicio.monto}\n"
                    f"- Fecha: {instance.horario.fecha}\n"
                    f"- Código: {instance.token}\n\n"
                    f"Gracias por elegirnos."
                )
            elif new_estado == 'pendiente':
                cambiado_por = f"por el trabajador {new_trabajador.user.username}" if new_trabajador else "por un administrador"
                asunto = 'Tu reserva está pendiente'
                mensaje = (
                    f"Hola {instance.nombre},\n\n"
                    f"Tu reserva fue marcada como pendiente {cambiado_por}.\n"
                    f"- Servicio: {instance.servicio.nombre}\n"
                    f"- Fecha: {instance.horario.fecha}\n"
                    f"- Código: {instance.token}\n\n"
                    f"Te informaremos de los próximos pasos."
                )
            elif new_estado == 'cancelado':
                cambiado_por = f"por el trabajador {new_trabajador.user.username}" if new_trabajador else "por un administrador"
                asunto = '¡Tu reserva ha sido cancelada!'
                mensaje = (
                    f"Hola {instance.nombre},\n\n"
                    f"Tu reserva fue cancelada {cambiado_por}.\n"
                    f"- Servicio: {instance.servicio.nombre}\n"
                    f"- Fecha: {instance.horario.fecha}\n"
                    f"- Código: {instance.token}\n\n"
                    f"Contáctanos si tienes preguntas."
                )
            elif new_estado == 'confirmado' and old_trabajador is None:
                asunto = '¡Reserva confirmada por administrador!'
                mensaje = (
                    f"Hola {instance.nombre},\n\n"
                    f"Tu reserva fue confirmada por un administrador.\n"
                    f"- Servicio: {instance.servicio.nombre}\n"
                    f"- Fecha: {instance.horario.fecha}\n"
                    f"- Código: {instance.token}\n"
                )
            elif new_estado == 'confirmado' and new_trabajador:
                asunto = '¡Tu reserva fue aceptada!'
                mensaje = (
                    f"Hola {instance.nombre},\n\n"
                    f"Tu reserva ha sido aceptada y asignada a {new_trabajador.user.username}.\n"
                    f"- Servicio: {instance.servicio.nombre}\n"
                    f"- Fecha: {instance.horario.fecha}\n"
                    f"- Código: {instance.token}\n"
                )
        elif old_trabajador != new_trabajador:
            if new_trabajador:
                asunto = '¡Trabajador asignado!'
                mensaje = (
                    f"Hola {instance.nombre},\n\n"
                    f"Un trabajador fue asignado: {new_trabajador.user.username}.\n"
                    f"- Servicio: {instance.servicio.nombre}\n"
                    f"- Fecha: {instance.horario.fecha}\n"
                    f"- Código: {instance.token}\n"
                )
            else:
                asunto = 'Trabajador desasignado'
                mensaje = (
                    f"Hola {instance.nombre},\n\n"
                    f"Tu reserva ya no tiene trabajador asignado.\n"
                    f"- Servicio: {instance.servicio.nombre}\n"
                    f"- Código: {instance.token}\n"
                )

    if asunto and mensaje:
        try:
            from django.core.mail import EmailMessage

            email = EmailMessage(
                subject=asunto,
                body=mensaje,
                from_email=EMAIL_HOST_USER,
                to=[instance.email],
            )
            email.encoding = 'utf-8'
            email.send()
        except Exception as e:
            print(f"ERROR enviando correo: {e}")
            raise EmailSendingError("Error al enviar el correo electrónico.")
