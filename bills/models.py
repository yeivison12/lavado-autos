from django.db import models
from simple_history.models import HistoricalRecords 
from workers.models import Worker

class Recibo(models.Model):
    reserva = models.OneToOneField('orders.Reserva', on_delete=models.CASCADE, related_name="recibo")
    trabajador = models.ForeignKey(Worker, null=True, blank=True, on_delete=models.SET_NULL, related_name="recibos")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    comentario = models.TextField(blank=True, null=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    historial = HistoricalRecords()
    def __str__(self):
        trabajador_nombre = self.trabajador.user.username if self.trabajador else "No asignado"
        return f"Recibo {self.id} - {self.reserva.nombre} - ${self.monto} - {trabajador_nombre}"


class Tarifa(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='tarifas/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    historial = HistoricalRecords()
    
    def __str__(self):
        return f"{self.nombre} - ${self.monto}"

