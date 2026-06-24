import unittest
from unittest.mock import Mock
from datetime import datetime, timedelta
from app.domain.entities.requerimiento import Incidente, Solicitud
from app.domain.entities.usuario import Solicitante, Tecnico, Operador
from app.domain.enums import NivelUrgencia, CategoriaIncidente, CategoriaSolicitud, EstadoRequerimiento
from app.domain.exceptions import EstadoInvalidoException


class TestRequerimientos(unittest.TestCase):

    def setUp(self):
        # Mocks puros
        self.solicitante_mock = Mock(spec=Solicitante)
        self.solicitante_mock.id = 1

        self.tecnico_mock = Mock(spec=Tecnico)
        self.tecnico_mock.id = 2

        self.operador_mock = Mock(spec=Operador)
        self.operador_mock.id = 3

    def test_calculo_prioridad_incidente(self):
        fecha_hace_2_dias = datetime.now() - timedelta(days=2)

        incidente = Incidente(
            id=1, titulo="Falla", descripcion="Descripcion valida",
            solicitante=self.solicitante_mock,
            nivel_urgencia=NivelUrgencia.CRITICO,
            categoria=CategoriaIncidente.SERVICIO_INACCESIBLE,
            fecha_creacion=fecha_hace_2_dias
        )

        # 100 (Critico) + 2 (días) = 102
        self.assertEqual(incidente.calcular_prioridad(), 102)

    def test_calculo_prioridad_solicitud(self):
        fecha_hace_10_dias = datetime.now() - timedelta(days=10)

        solicitud = Solicitud(
            id=2, titulo="Titulo", descripcion="Descripcion valida",
            solicitante=self.solicitante_mock,
            categoria=CategoriaSolicitud.ALTA_SERVICIO,
            fecha_creacion=fecha_hace_10_dias
        )

        self.assertEqual(solicitud.calcular_prioridad(), 10)

    def test_ciclo_vida_correcto(self):
        req = Incidente(1, "Titulo", "Descripcion", self.solicitante_mock,
                        NivelUrgencia.MENOR, CategoriaIncidente.BLOQUEO_SIM)

        # 1. Asignación con mocks
        req.asignar_tecnico(self.tecnico_mock, self.operador_mock)

        self.assertEqual(req.estado, EstadoRequerimiento.ASIGNADO)
        self.assertIs(req.tecnico_asignado, self.tecnico_mock)

        # 2. Resolución
        req.resolver(self.tecnico_mock)
        self.assertEqual(req.estado, EstadoRequerimiento.RESUELTO)
        self.assertIsNotNone(req.fecha_resolucion)

    def test_transicion_estado_invalida(self):
        req = Incidente(1, "Titulo", "Descripcion", self.solicitante_mock, NivelUrgencia.MENOR, "CAT")

        # Forzamos estado
        req.estado = EstadoRequerimiento.RESUELTO

        with self.assertRaises(EstadoInvalidoException):
            req.asignar_tecnico(self.tecnico_mock, self.operador_mock)