import unittest
from datetime import datetime
from app.domain.entities.notificacion import Notificacion
from app.domain.entities.usuario import Supervisor


class TestNotificacion(unittest.TestCase):
    def setUp(self):
        self.supervisor = Supervisor(1, "Jefe", None, "pass")
        # Mock de evento
        self.evento_mock = type('EventoMock', (), {'get_descripcion_detallada': lambda: "Algo pasó"})()

    def test_notificacion_inicia_no_leida(self):
        """Por defecto una notificación debe estar no leída"""
        notif = Notificacion(1, self.evento_mock, self.supervisor)
        self.assertFalse(notif.es_leida())
        self.assertIsNone(notif.fecha_lectura)

    def test_marcar_como_leida(self):
        """Marcar como leída debe cambiar el estado y setear fecha"""
        notif = Notificacion(1, self.evento_mock, self.supervisor)

        notif.marcar_como_leida()

        self.assertTrue(notif.es_leida())
        self.assertIsNotNone(notif.fecha_lectura)
        self.assertIsInstance(notif.fecha_lectura, datetime)

    def test_marcar_leida_idempotente(self):
        """Marcar como leída una notificación ya leída no debe cambiar la fecha original"""
        notif = Notificacion(1, self.evento_mock, self.supervisor)
        notif.marcar_como_leida()
        fecha_original = notif.fecha_lectura

        # Intentar marcar de nuevo
        notif.marcar_como_leida()

        self.assertEqual(notif.fecha_lectura, fecha_original)