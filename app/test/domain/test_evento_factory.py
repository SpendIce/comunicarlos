import unittest
from app.domain.factories.evento_factory import EventoFactory
from app.domain.entities.evento import EventoDerivacion, EventoAsignacion
from app.domain.entities.usuario import Operador, Tecnico
from app.domain.value_objects.email import Email
from app.domain.enums import TipoEvento


class TestEventoFactory(unittest.TestCase):

    def setUp(self):
        # Mocks mínimos necesarios
        self.op = Operador(1, "Op", Email("op@comunicarlos.com.ar"), "pw")
        self.tec1 = Tecnico(2, "T1", Email("t1@comunicarlos.com.ar"), "pw")
        self.tec2 = Tecnico(3, "T2", Email("t2@comunicarlos.com.ar"), "pw")
        self.req = "MockRequerimiento"  # El factory no valida el tipo del req, solo lo pasa

    def test_creacion_evento_asignacion(self):
        """Factory debe crear EventoAsignacion con los parámetros correctos"""
        evento = EventoFactory.crear_evento(
            TipoEvento.ASIGNACION,
            requerimiento=self.req,
            responsable=self.op,
            tecnico_asignado=self.tec1
        )

        self.assertIsInstance(evento, EventoAsignacion)
        self.assertEqual(evento.tecnico_asignado, self.tec1)

    def test_creacion_evento_derivacion_incompleta(self):
        """Factory debe validar parámetros obligatorios (motivo, destino)"""
        with self.assertRaises(ValueError):
            EventoFactory.crear_evento(
                TipoEvento.DERIVACION,
                requerimiento=self.req,
                responsable=self.tec1,
                # Falta tecnico_destino y motivo
                tecnico_origen=self.tec1
            )

    def test_tipo_evento_desconocido(self):
        """Debe fallar si le pasamos un enum que no maneja"""
        with self.assertRaises(ValueError):
            EventoFactory.crear_evento("TIPO_INEXISTENTE", self.req, self.op)