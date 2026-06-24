from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List
from app.domain.enums import TipoUsuario
from app.domain.value_objects.email import Email
from app.domain.exceptions import EmailInvalidoException


class Usuario(ABC):
    """
    Clase Abstracta Base (ABC) para todos los actores del sistema.

    Concepto POO: Abstracción. Definimos el contrato base (nombre, email, password)
    y obligamos a las subclases a implementar métodos de permisos específicos
    como 'puede_ver_requerimiento', garantizando polimorfismo.
    """

    def __init__(
            self,
            id: Optional[int],
            nombre: str,
            email: Email,
            password_hash: str,
            fecha_creacion: Optional[datetime] = None,
            ultimo_acceso: Optional[datetime] = None
    ):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password_hash = password_hash  # La encriptación (Bcrypt) se maneja en la capa de servicio/infra
        self.fecha_creacion = fecha_creacion or datetime.now()
        self.ultimo_acceso = ultimo_acceso

    def actualizar_ultimo_acceso(self) -> None:
        """Auditabilidad: Registra cuándo fue la última vez que el usuario ingresó."""
        self.ultimo_acceso = datetime.now()

    @abstractmethod
    def get_tipo_usuario(self) -> TipoUsuario:
        pass

    @abstractmethod
    def puede_ver_requerimiento(self, requerimiento) -> bool:
        """Define la política de visibilidad según el rol (Polimorfismo)."""
        pass

    def __str__(self) -> str:
        return f"{self.nombre} <{self.email}>"


class Solicitante(Usuario):
    """
    Representa al empleado/cliente que reporta problemas.
    Regla: Solo puede ver y gestionar sus propios recursos.
    """

    def __init__(self, id, nombre, email, password_hash, servicios_suscritos=None, **kwargs):
        super().__init__(id, nombre, email, password_hash, **kwargs)
        self.servicios_suscritos = servicios_suscritos or []

    def get_tipo_usuario(self) -> TipoUsuario:
        return TipoUsuario.SOLICITANTE

    def puede_ver_requerimiento(self, requerimiento) -> bool:
        # Regla de privacidad: Solo ve lo suyo
        return requerimiento.solicitante.id == self.id


class EmpleadoSoporte(Usuario, ABC):
    """
    Clase intermedia para agrupar lógica común de empleados técnicos.
    Regla: Validación estricta de email corporativo.
    """

    def __init__(self, id, nombre, email, password_hash, **kwargs):
        if not email.es_corporativo():
            raise EmailInvalidoException("El personal de soporte debe usar email @comunicarlos.com.ar")
        super().__init__(id, nombre, email, password_hash, **kwargs)


class Operador(EmpleadoSoporte):
    """Rol: Mesa de ayuda (Nivel 1). Triaje y asignación."""

    def get_tipo_usuario(self) -> TipoUsuario:
        return TipoUsuario.OPERADOR

    def puede_ver_requerimiento(self, requerimiento) -> bool:
        # Los operadores tienen visibilidad total para poder asignar
        return True


class Tecnico(EmpleadoSoporte):
    """Rol: Especialista (Nivel 2). Resolución técnica."""

    def __init__(self, id, nombre, email, password_hash, especialidades=None, **kwargs):
        super().__init__(id, nombre, email, password_hash, **kwargs)
        self.especialidades = especialidades or []

    def get_tipo_usuario(self) -> TipoUsuario:
        return TipoUsuario.TECNICO

    def puede_ver_requerimiento(self, requerimiento) -> bool:
        # Regla: Solo ven lo que tienen asignado (encapsulamiento de trabajo)
        return requerimiento.tecnico_asignado and requerimiento.tecnico_asignado.id == self.id

    def tiene_especialidad(self, especialidad: str) -> bool:
        return especialidad in self.especialidades


class Supervisor(Usuario):
    """Rol: Auditoría y Control. Solo lectura y notificaciones."""

    def __init__(self, id, nombre, email, password_hash, operadores_supervisados=None, tecnicos_supervisados=None,
                 **kwargs):
        super().__init__(id, nombre, email, password_hash, **kwargs)
        self.operadores_supervisados = operadores_supervisados or []
        self.tecnicos_supervisados = tecnicos_supervisados or []
        self.notificaciones = []

    def get_tipo_usuario(self) -> TipoUsuario:
        return TipoUsuario.SUPERVISOR

    def puede_ver_requerimiento(self, requerimiento) -> bool:
        return True  # Supervisión total