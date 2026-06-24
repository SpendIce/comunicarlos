import unittest
from app.domain.entities.usuario import Solicitante, Operador, Tecnico, Supervisor
from app.domain.entities.requerimiento import Incidente
from app.domain.value_objects.email import Email
from app.domain.enums import NivelUrgencia, CategoriaIncidente
from app.domain.exceptions import EmailInvalidoException


class TestUsuarios(unittest.TestCase):

    def setUp(self):
        """Configuración previa para cada test"""
        self.email_sol = Email("user@gmail.com")
        self.email_corp = Email("staff@comunicarlos.com.ar")

        self.solicitante_1 = Solicitante(1, "Juan", self.email_sol, "hash")
        self.solicitante_2 = Solicitante(2, "Pedro", Email("pedro@gmail.com"), "hash")

        self.tecnico = Tecnico(3, "Tecnico1", self.email_corp, "hash")
        self.operador = Operador(4, "Operador1", self.email_corp, "hash")

        # Mock básico de requerimiento
        self.req_propio = Incidente(1, "Titulo", "Descripcion", self.solicitante_1,
                                    NivelUrgencia.MENOR, CategoriaIncidente.BLOQUEO_SIM)

    def test_validacion_email_empleados(self):
        """Los empleados NO pueden tener email personal (Regla de Negocio)"""
        with self.assertRaises(EmailInvalidoException):
            Tecnico(5, "Falso", self.email_sol, "hash")

    def test_permisos_visualizacion_solicitante(self):
        """El solicitante solo ve sus propios requerimientos (Encapsulamiento)"""
        self.assertTrue(self.solicitante_1.puede_ver_requerimiento(self.req_propio))
        self.assertFalse(self.solicitante_2.puede_ver_requerimiento(self.req_propio))

    def test_permisos_visualizacion_tecnico(self):
        """El técnico solo ve lo que tiene asignado"""
        self.assertFalse(self.tecnico.puede_ver_requerimiento(self.req_propio))

        self.req_propio.tecnico_asignado = self.tecnico
        self.assertTrue(self.tecnico.puede_ver_requerimiento(self.req_propio))

    def test_permisos_visualizacion_operador(self):
        """El operador debe ver todo para poder triar"""
        self.assertTrue(self.operador.puede_ver_requerimiento(self.req_propio))