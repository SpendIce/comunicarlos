import unittest
from app.domain.entities.evento import (
    EventoCreacion, EventoAsignacion, EventoDerivacion, EventoResolucion
)
from app.domain.entities.usuario import Solicitante, Operador, Tecnico
from app.domain.value_objects.email import Email
from app.domain.enums import TipoEvento

class TestEventosLogica(unittest.TestCase):
    def setUp(self):
        self.solicitante = Solicitante(1, "Ana", Email("a@a.com"), "")
        self.operador = Operador(2, "Op", Email("op@comunicarlos.com.ar"), "")
        self.tecnico1 = Tecnico(3, "Tec1", Email("t1@comunicarlos.com.ar"), "")
        self.tecnico2 = Tecnico(4, "Tec2", Email("t2@comunicarlos.com.ar"), "")
        self.req_mock = type('ReqMock', (), {'id': 99})

    def test_descripcion_creacion(self):
        ev = EventoCreacion(1, self.solicitante, self.req_mock)
        self.assertIn("dado de alta", ev.get_descripcion_detallada())
        self.assertIn("Ana", ev.get_descripcion_detallada())
        self.assertEqual(ev.get_tipo_evento(), TipoEvento.CREACION)

    def test_descripcion_asignacion(self):
        ev = EventoAsignacion(1, self.operador, self.req_mock, self.tecnico1)
        desc = ev.get_descripcion_detallada()
        self.assertIn("Op", desc)
        self.assertIn("asignó", desc)
        self.assertIn("Tec1", desc)

    def test_descripcion_derivacion(self):
        motivo = "No tengo las herramientas"
        ev = EventoDerivacion(1, self.tecnico1, self.req_mock, self.tecnico1, self.tecnico2, motivo)
        desc = ev.get_descripcion_detallada()
        self.assertIn("Tec1", desc)
        self.assertIn("Tec2", desc)
        self.assertIn(motivo, desc)
