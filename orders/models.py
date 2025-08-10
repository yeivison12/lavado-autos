from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid
from simple_history.models import HistoricalRecords

from workers.models import Worker   

class HorarioDisponible(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    disponible = models.BooleanField(default=True)

    class Meta:
        unique_together = ('fecha', 'hora')  
        ordering = ['fecha', 'hora']
        verbose_name = "Horario Disponible"
        verbose_name_plural = "Horarios Disponibles"

    def __str__(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return f"{self.fecha} {self.hora} - {estado}"

    def marcar_no_disponible(self):
        self.disponible = False
        self.save()

    def marcar_disponible(self):
        self.disponible = True
        self.save()

    def clean(self):
        # Validación: No se puede seleccionar una fecha en el pasado
        if self.fecha < timezone.now().date():
            raise ValidationError("No se puede seleccionar una fecha en el pasado.")

        # Validación: Evitar duplicados de fecha y hora
        if HorarioDisponible.objects.filter(fecha=self.fecha, hora=self.hora).exclude(pk=self.pk).exists():
            raise ValidationError("Ya existe un horario disponible con esta fecha y hora.")

        super().clean()

    def delete(self, *args, **kwargs):
        if self.reservas.exists():  # Verifica si hay reservas asociadas
            raise ValidationError("No se puede eliminar este horario porque está siendo utilizado por una reserva.")
        super().delete(*args, **kwargs)

class Reserva(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('completado', 'Completado'),
    ]

    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=250, blank=True)
    historial = HistoricalRecords()
    telefono = models.CharField(
        max_length=25,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="El número de teléfono debe estar en el formato: '+999999999'. Hasta 15 dígitos permitidos."
        )]
    )
    servicio = models.ForeignKey(
        'bills.Tarifa',
        on_delete=models.PROTECT,
        related_name="reservas",
        verbose_name="Servicio"
    )
    horario = models.ForeignKey(
        HorarioDisponible,
        on_delete=models.PROTECT,
        related_name="reservas",
        verbose_name="Horario"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    trabajador = models.ForeignKey(Worker, null=True, blank=True, on_delete=models.SET_NULL, related_name='reservas')

    def __str__(self):
        return f'{self.nombre} - {self.servicio} - {self.horario.fecha} {self.horario.hora}'

    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado in dict(self.ESTADOS).keys():
            self.estado = nuevo_estado
            self.save()
        else:
            raise ValueError("Estado no válido")

    def clean(self):
        # Validación solo para nuevas reservas
        if self.pk is None:
            if self.horario_id is None:
                raise ValidationError({'horario': "Debes seleccionar un horario."})
            elif not self.horario.disponible:
                raise ValidationError({'horario': "El horario seleccionado no está disponible."})
        super().clean()

    def save(self, *args, **kwargs):
        # Validación y marcado de horario como no disponible solo para nuevas reservas
        if self.pk is None:
            if not self.horario.disponible:
                raise ValidationError({'horario': "El horario seleccionado no está disponible."})
            self.horario.marcar_no_disponible()
        super().save(*args, **kwargs)

    def actualizar_horario(self, nuevo_horario):
        """
        Actualiza el horario de la reserva.
        Marca el horario anterior como disponible y el nuevo como no disponible.
        """
        if self.horario != nuevo_horario:
            # Liberar el horario anterior
            self.horario.marcar_disponible()
            # Asignar el nuevo horario
            self.horario = nuevo_horario
            self.horario.marcar_no_disponible()
            self.save()

    def delete(self, *args, **kwargs):
        # Marcar el horario como disponible antes de eliminar la reserva
        self.horario.marcar_disponible()
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"