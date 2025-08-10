from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Worker
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed
from django.contrib.auth import get_user_model

@receiver(user_logged_in)
def actualizar_estado_conectado(sender, user, request, **kwargs):
    if hasattr(user, 'worker'):
        user.worker.cambiar_estado('conectado')

@receiver(user_logged_out)
def actualizar_estado_desconectado(sender, user, request, **kwargs):
    if hasattr(user, 'worker'):
        user.worker.cambiar_estado('desconectado')
@receiver(pre_save, sender=Worker)
def actualizar_estado_ocupado(sender, instance, **kwargs):
    if instance.servicio_actual:
        instance.estado = 'ocupado'

User = get_user_model()

@receiver(m2m_changed, sender=User.groups.through)
def create_worker_profile_on_group_add(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        trabajadores_group = Group.objects.filter(name='Trabajadores').first()
        if trabajadores_group and trabajadores_group.id in pk_set:
            if not hasattr(instance, 'worker'):
                Worker.objects.create(user=instance, estado='desconectado')