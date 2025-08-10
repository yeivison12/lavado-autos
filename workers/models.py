from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
class Worker(models.Model):
    ESTADOS = [
        ('conectado', 'Conectado'),
        ('ausente', 'Ausente'),
        ('ocupado', 'Ocupado'),
        ('desconectado', 'Desconectado'),
        ('hora de comida', 'Hora de Comida'),  
    ]

    def custom_upload_to(instance, filename):
        try:
            old_instance = Worker.objects.get(pk=instance.pk)
            if old_instance.avatar:
                old_instance.avatar.delete(save=False)
        except Worker.DoesNotExist:
            pass
        return 'profiles/' + filename
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worker')
    avatar = models.ImageField(upload_to=custom_upload_to, null=True, blank=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='desconectado')
    servicio_actual = models.ForeignKey('orders.Reserva', null=True, blank=True, on_delete=models.SET_NULL, related_name='workerAsignado')
    bio = models.TextField(null=True, blank=True)
    historial = HistoricalRecords()
    
    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado in dict(self.ESTADOS).keys():
            self.estado = nuevo_estado
            self.save()
        else:
            raise ValueError("Estado no válido")
    def esta_disponible(self):
        return self.estado == 'conectado' and self.servicio_actual is None


    def __str__(self):
        return f'{self.user.username} - {self.get_estado_display()}'