import unittest
from unittest.mock import Mock
from datetime import datetime
from app.domain.entities.comentario import Comentario
from app.domain.entities.usuario import Tecnico
from app.domain.entities.requerimiento import Requerimiento


class TestComentario(unittest.TestCase):
    def setUp(self):
        # --- Mocking ---
        # Mock del Autor (Técnico)
        self.autor_mock = Mock(spec=Tecnico)
        self.autor_mock.nombre = "Pepe"
        self.autor_mock.id = 1

        # Mock del Requerimiento
        self.req_mock = Mock(spec=Requerimiento)
        self.req_mock.id = 100

    def test_creacion_comentario(self):
        """El comentario debe almacenar correctamente texto, autor y fecha"""
        texto = "Este es un comentario de prueba"
        fecha = datetime(2023, 1, 1, 12, 0, 0)

        comentario = Comentario(
            id=1,
            texto=texto,
            autor=self.autor_mock,
            requerimiento=self.req_mock,
            fecha_hora=fecha
        )

        self.assertEqual(comentario.texto, texto)
        # Verificamos identidad de los objetos
        self.assertIs(comentario.autor, self.autor_mock)
        self.assertIs(comentario.requerimiento, self.req_mock)
        self.assertEqual(comentario.fecha_hora, fecha)

    def test_str_representation(self):
        """Verificar la representación en string del comentario"""
        # Según tu código: return f"{self.autor.nombre}: {self.texto[:20]}..."
        texto_largo = "Texto largo para probar el truncado del string"
        comentario = Comentario(1, texto_largo, self.autor_mock, self.req_mock)

        resultado_str = str(comentario)

        self.assertIn("Pepe", resultado_str)
        self.assertIn("Texto largo", resultado_str)