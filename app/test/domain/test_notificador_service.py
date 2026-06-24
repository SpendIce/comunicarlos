import unittest
from unittest.mock import Mock, AsyncMock
from app.domain.services.notificador import Notificador
from app.domain.entities.evento import Evento
from app.domain.entities.usuario import Tecnico, Supervisor
from app.domain.entities.notificacion import Notificacion
from app.domain.value_objects.email import Email


class TestNotificadorService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # --- Mocks de Dependencias (Repositorios y Secuencia) ---
        self.user_repo_mock = Mock()
        self.notif_repo_mock = Mock()
        self.sequence_mock = Mock()

        # Configurar comportamiento asíncrono
        self.user_repo_mock.buscar_supervisores_de_empleado = AsyncMock()
        self.notif_repo_mock.guardar = AsyncMock()
        self.sequence_mock.get_next = AsyncMock(return_value=123)

        # Instanciar el servicio bajo prueba (System Under Test)
        self.notificador = Notificador(
            self.user_repo_mock,
            self.notif_repo_mock,
            self.sequence_mock
        )

        # --- Mocks de Entidades de Dominio ---
        # Mock del Email para pasar la validación del constructor de Tecnico
        self.email_mock = Mock(spec=Email)
        self.email_mock.es_corporativo.return_value = True  # Simula ser corporativo
        self.email_mock.__str__ = Mock(return_value="tec@comunicarlos.com.ar")

        # Ahora podemos instanciar Tecnico sin que explote la validación
        self.tecnico = Tecnico(1, "Tec", self.email_mock, "password_hash")

        # Mock del Evento
        self.evento_mock = Mock(spec=Evento)
        self.evento_mock.responsable = self.tecnico

    async def test_notificar_evento_con_supervisores(self):
        """Debe crear y guardar notificaciones si el usuario tiene supervisores"""
        # Arrange: Simulamos que el repo encuentra un supervisor
        supervisor_mock = Mock(spec=Supervisor)
        self.user_repo_mock.buscar_supervisores_de_empleado.return_value = [supervisor_mock]

        # Act
        await self.notificador.notificar_evento(self.evento_mock)

        # Assert
        self.user_repo_mock.buscar_supervisores_de_empleado.assert_awaited_once_with(self.tecnico.id)
        self.sequence_mock.get_next.assert_awaited_once()
        self.notif_repo_mock.guardar.assert_awaited_once()

        # Verificamos que lo que se intentó guardar sea una Notificación
        args, _ = self.notif_repo_mock.guardar.call_args
        notificacion_guardada = args[0]
        self.assertIsInstance(notificacion_guardada, Notificacion)
        self.assertEqual(notificacion_guardada.supervisor, supervisor_mock)

    async def test_no_notificar_sin_supervisores(self):
        """No debe hacer nada si el usuario no tiene supervisores"""
        # Arrange: Simulamos lista vacía
        self.user_repo_mock.buscar_supervisores_de_empleado.return_value = []

        # Act
        await self.notificador.notificar_evento(self.evento_mock)

        # Assert: No se debe haber llamado a guardar ni generado ID
        self.notif_repo_mock.guardar.assert_not_called()
        self.sequence_mock.get_next.assert_not_called()