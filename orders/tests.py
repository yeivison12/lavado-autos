from django.test import TestCase
from django.core import mail
from django.contrib.auth.models import User, Group
from orders.models import Reserva, HorarioDisponible  # Importar HorarioDisponible en lugar de Horario
from django.utils import timezone

class ReservaSignalsTestCase(TestCase):
    def setUp(self):
        # Crear un usuario administrador
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='adminpass')
        self.admin_user.is_staff = True
        self.admin_user.save()

        # Crear un usuario trabajador
        self.worker_user = User.objects.create_user(username='worker', email='worker@example.com', password='workerpass')
        
        # Verificar si el grupo "Trabajadores" ya existe antes de crearlo
        trabajadores_group, created = Group.objects.get_or_create(name='Trabajadores')
        self.worker_user.groups.add(trabajadores_group)
        self.worker_user.save()

        # Crear un horario disponible
        self.horario = HorarioDisponible.objects.create(fecha=timezone.now().date(), hora=timezone.now().time())

        # Crear una reserva
        self.reserva = Reserva.objects.create(
            nombre='Cliente',
            email='cliente@example.com',
            servicio='basico',
            horario=self.horario,
            estado='pendiente'
        )

    def test_reserva_confirmada_por_admin(self):
        # Cambiar el estado de la reserva a 'confirmado' por el administrador
        self.client.login(username='admin', password='adminpass')
        self.reserva.estado = 'confirmado'
        self.reserva.save()

        # Verificar que se envió un correo
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('¡Tu reserva ha sido confirmada!', mail.outbox[0].subject)

    def test_reserva_asignada_a_trabajador(self):
        # Cambiar el estado de la reserva a 'confirmado' y asignar un trabajador
        self.client.login(username='admin', password='adminpass')
        self.reserva.estado = 'confirmado'
        self.reserva.trabajador = self.worker_user.worker
        self.reserva.save()

        # Verificar que se envió un correo
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('¡Tu reserva ha sido aceptada y asignada!', mail.outbox[0].subject)

    def test_reserva_completada(self):
        # Cambiar el estado de la reserva a 'completado'
        self.client.login(username='worker', password='workerpass')
        self.reserva.estado = 'confirmado'
        self.reserva.trabajador = self.worker_user.worker
        self.reserva.save()

        self.reserva.estado = 'completado'
        self.reserva.save()

        # Verificar que se envió un correo
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('¡Tu reserva ha sido completada!', mail.outbox[0].subject)

    def test_reserva_cancelada(self):
        # Cambiar el estado de la reserva a 'pendiente' (cancelada)
        self.client.login(username='worker', password='workerpass')
        self.reserva.estado = 'confirmado'
        self.reserva.trabajador = self.worker_user.worker
        self.reserva.save()

        self.reserva.estado = 'pendiente'
        self.reserva.trabajador = None
        self.reserva.save()

        # Verificar que se envió un correo
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('¡Tu reserva ha sido cancelada!', mail.outbox[0].subject)