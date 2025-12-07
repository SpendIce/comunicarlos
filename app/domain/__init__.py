"""
Capa de Dominio - Sistema de Mesa de Ayuda

Esta capa contiene toda la lógica de negocio del sistema.
Es independiente de infraestructura (base de datos, frameworks, etc.)
"""

from app.domain.entities.usuario import (
    Usuario,
    Solicitante,
    Operador,
    Tecnico,
    Supervisor,
    EmpleadoSoporte
)
from app.domain.entities.requerimiento import (
    Requerimiento,
    Incidente,
    Solicitud
)
from app.domain.entities.comentario import Comentario
from app.domain.entities.evento import (
    Evento,
    EventoCreacion,
    EventoAsignacion,
    EventoDerivacion,
    EventoResolucion,
    EventoReapertura,
    EventoComentario
)
from app.domain.entities.servicio import Servicio
from app.domain.entities.notificacion import Notificacion
from app.domain.factories.evento_factory import EventoFactory
from app.domain.services.notificador import Notificador
from app.domain.value_objects.email import Email
from app.domain.exceptions import (
    RequerimientoException,
    EstadoInvalidoException,
    PermisosDenegadosException,
    ValidacionException,
    UsuarioException,
    EmailInvalidoException,
    ServicioException
)

__all__ = [
    # Usuarios
    'Usuario',
    'Solicitante',
    'Operador',
    'Tecnico',
    'Supervisor',
    'EmpleadoSoporte',

    # Value Objects
    'Email',

    # Requerimientos
    'Requerimiento',
    'Incidente',
    'Solicitud',

    # Otros
    'Comentario',
    'Servicio',
    'Notificacion',

    # Eventos
    'Evento',
    'EventoCreacion',
    'EventoAsignacion',
    'EventoDerivacion',
    'EventoResolucion',
    'EventoReapertura',
    'EventoComentario',

    # Factories y Services
    'EventoFactory',
    'Notificador',

    # Excepciones
    'RequerimientoException',
    'EstadoInvalidoException',
    'PermisosDenegadosException',
    'ValidacionException',
    'UsuarioException',
    'EmailInvalidoException',
    'ServicioException',
]
