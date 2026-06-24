import unittest
from app.domain.value_objects.email import Email
from app.domain.exceptions import EmailInvalidoException


class TestEmail(unittest.TestCase):

    def test_creacion_email_valido(self):
        """Debe crear correctamente un email con formato válido"""
        email = Email("usuario@ejemplo.com")
        self.assertEqual(email.valor, "usuario@ejemplo.com")
        self.assertEqual(str(email), "usuario@ejemplo.com")

    def test_validacion_formato_invalido(self):
        """Debe lanzar excepción si el formato es incorrecto"""
        emails_invalidos = ["sin_arroba", "usuario@", "@dominio.com", "u s@d.com"]

        for e in emails_invalidos:
            with self.assertRaises(EmailInvalidoException):
                Email(e)

    def test_identificacion_corporativa(self):
        """Debe distinguir entre emails corporativos y externos"""
        corp = Email("admin@comunicarlos.com.ar")
        externo = Email("cliente@gmail.com")

        self.assertTrue(corp.es_corporativo())
        self.assertFalse(externo.es_corporativo())