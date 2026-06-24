import unittest
from unittest.mock import Mock
from app.domain.entities.servicio import Servicio
from app.domain.entities.usuario import Solicitante
from app.domain.enums import TipoServicio
from app.domain.exceptions import ServicioException

class TestServicio(unittest.TestCase):

    def setUp(self):
        # Mock del propietario del servicio
        self.solicitante_mock = Mock(spec=Solicitante)

    def test_activacion_desactivacion(self):
        """Prueba las transiciones de estado del servicio"""
        servicio = Servicio(
            id=1,
            tipo=TipoServicio.INTERNET_BANDA_ANCHA,
            numero_servicio="12345",
            solicitante=self.solicitante_mock, # Usamos Mock
            activo=True
        )

        # Desactivar
        servicio.desactivar()
        self.assertFalse(servicio.activo)

        # Activar
        servicio.activar()
        self.assertTrue(servicio.activo)

    def test_activar_servicio_ya_activo(self):
        """No debe permitir activar lo que ya está activo"""
        servicio = Servicio(1, TipoServicio.TELEVISION, "12345", self.solicitante_mock, activo=True)

        with self.assertRaises(ServicioException):
            servicio.activar()