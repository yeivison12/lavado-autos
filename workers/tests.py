from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.apps import apps
from workers.models import Worker
from orders.models import Reserva, HorarioDisponible

class WorkerViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='texer', password='12345')
        self.group, created = Group.objects.get_or_create(name='Trabajadores')
        self.user.groups.add(self.group)
        self.worker = Worker.objects.create(user=self.user, estado='conectado')
        self.horario = HorarioDisponible.objects.create(fecha='2025-02-12', hora='10:00:00', disponible=True)
        self.reserva = Reserva.objects.create(
            nombre='Test Reserva',
            email='test@example.com',
            telefono='+123456789',
            servicio='basico',
            horario=self.horario,
            estado='confirmado'
        )

    def test_aceptar_orden_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('aceptar_orden', args=[self.reserva.id]))
        self.reserva.refresh_from_db()
        self.worker.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.reserva.estado, 'confirmado')
        self.assertEqual(self.reserva.trabajador, self.worker)
        self.assertEqual(self.worker.servicio_actual, self.reserva)

    def test_completar_orden_view(self):
        self.client.login(username='testuser', password='12345')
        self.worker.servicio_actual = self.reserva
        self.worker.save()
        response = self.client.post(reverse('completar_orden', args=[self.reserva.id]))
        self.reserva.refresh_from_db()
        self.worker.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.reserva.estado, 'completado')
        self.assertIsNone(self.worker.servicio_actual)
        self.assertEqual(self.worker.estado, 'conectado')

    def test_cancelar_orden_view(self):
        self.client.login(username='testuser', password='12345')
        self.worker.servicio_actual = self.reserva
        self.worker.save()
        response = self.client.post(reverse('cancelar_orden', args=[self.reserva.id]))
        self.reserva.refresh_from_db()
        self.worker.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.reserva.estado, 'confirmado')
        self.assertIsNone(self.reserva.trabajador)
        self.assertIsNone(self.worker.servicio_actual)
        self.assertEqual(self.worker.estado, 'conectado')