from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from app.domain.enums import TipoUsuario
from app.domain.value_objects.email import Email
from app.domain.exceptions import EmailInvalidoException


class Usuario(ABC):
    """Clase base abstracta para todos los tipos de usuario"""

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
        self.password_hash = password_hash
        self.fecha_creacion = fecha_creacion or datetime.now()
        self.ultimo_acceso = ultimo_acceso

    @abstractmethod
    def get_tipo_usuario(self) -> TipoUsuario:
        """Retorna el tipo de usuario"""
        pass

    @abstractmethod
    def puede_ver_requerimiento(self, requerimiento) -> bool:
        """Determina si el usuario puede ver un requerimiento"""
        pass

    @abstractmethod
    def puede_comentar_requerimiento(self, requerimiento) -> bool:
        """Determina si el usuario puede comentar en un requerimiento"""
        pass

    def actualizar_ultimo_acceso(self) -> None:
        """Actualiza la fecha de último acceso"""
        self.ultimo_acceso = datetime.now()

    def actualizar_nombre(self, nuevo_nombre: str) -> None:
        """Actualiza el nombre del usuario"""
        if len(nuevo_nombre) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
        self.nombre = nuevo_nombre

    def __str__(self) -> str:
        return f"{self.nombre} ({self.email})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, nombre='{self.nombre}')>"


class Solicitante(Usuario):
    """Usuario que reporta problemas y solicita servicios"""

    def __init__(
            self,
            id: Optional[int],
            nombre: str,
            email: Email,
            password_hash: str,
            servicios_suscritos: list = None,
            fecha_creacion: Optional[datetime] = None,
            ultimo_acceso: Optional[datetime] = None
    ):
        super().__init__(id, nombre, email, password_hash, fecha_creacion, ultimo_acceso)
        self.servicios_suscritos = servicios_suscritos or []
        self.requerimientos_creados = []

    def get_tipo_usuario(self) -> TipoUsuario:
        return TipoUsuario.SOLICITANTE

    def puede_ver_requerimiento(self, requerimiento) -> bool:
        """Solicitantes solo ven sus propios requerimientos"""
        return requerimiento.solicitante.id == self.id

    def puede_comentar_requerimiento(self, requerimiento) -> bool:
        """Solicitantes solo comentan en sus propios requerimientos"""
        return self.puede_ver_requerimiento(requerimiento)

    def tiene_servicio(self, tipo_servicio) -> bool:
        """Verifica si tiene un tipo de servicio específico"""
        return any(s.tipo == tipo_servicio for s in self.servicios_suscritos)

    def agregar_servicio(self, servicio) -> None:
        """Agrega un servicio a la lista de servicios suscritos"""
        if servicio not in self.servicios_suscritos:
            self.servicios_suscritos.append(servicio)


class EmpleadoSoporte(Usuario, ABC):
    """Clase base para empleados de soporte (Operador, Técnico)"""

    def __init__(
            self,
            id: Optional[int],
            nombre: str,
            email: Email,
            password_hash: str,
            fecha_creacion: Optional[datetime] = None,
            ultimo_acceso: Optional[datetime] = None
    ):
        super().__init__(id, nombre, email, password_hash, fecha_creacion, ultimo_acceso)

        # Validar email corporativo
        if not email.es_corporativo():
            raise EmailInvalidoException(
                f"Los empleados deben usar email corporativo @comunicarlos.com.ar"
            )


class Operador(EmpleadoSoporte):
    """Operador que asigna requerimientos a técnicos"""

    def __init__(
            self,
            id: Optional[int],
            nombre: str,
            email: Email,
            password_hash: str,
            fecha_creacion: Optional[datetime] = None,
            ultimo_acceso: Optional[datetime] = None
    ):
        super().__init__(id, nombre, email, password_hash, fecha_creacion, ultimo_acceso)
        self.requerimientos_gestionados = []

    def get_tipo_usuario(self) -> TipoUsuario:
        return TipoUsuario.OPERADOR

    def puede_ver_requerimiento(self, requerimiento) -> bool:
        """Operadores pueden ver todos los requerimientos"""
        return True

    def puede_comentar_requerimiento(self, requerimiento) -> bool:
        """Operadores pueden comentar en cualquier requerimiento"""
        return True

    def puede_asignar_requerimiento(self) -> bool:
        """Los operadores pueden asignar requerimientos"""
        return True

    def puede_reasignar_requerimiento(self) -> bool:
        """Los operadores pueden reasignar requerimientos"""
        return True


class Tecnico(EmpleadoSoporte):
    """Técnico que resuelve requerimientos"""

    def __init__(
            self,
            id: Optional[int],
            nombre: str,
            email: Email,
            password_hash: str,
            especialidades: list[str] = None,
            fecha_creacion: Optional[datetime] = None,
            ultimo_acceso: Optional[datetime] = None
    ):
        super().__init__(id, nombre, email, password_hash, fecha_creacion, ultimo_acceso)
        self.especialidades = especialidades or []
        self.requerimientos_asignados = []

    def get_tipo_usuario(self) -> TipoUsuario:
        return TipoUsuario.TECNICO

    def puede_ver_requerimiento(self, requerimiento) -> bool:
        """Técnicos solo ven requerimientos asignados a ellos"""
        return requerimiento.tecnico_asignado and requerimiento.tecnico_asignado.id == self.id

    def puede_comentar_requerimiento(self, requerimiento) -> bool:
        """Técnicos solo comentan en requerimientos asignados a ellos"""
        return self.puede_ver_requerimiento(requerimiento)

    def puede_resolver_requerimiento(self, requerimiento) -> bool:
        """Solo puede resolver si está asignado a él"""
        return self.puede_ver_requerimiento(requerimiento)

    def puede_derivar_requerimiento(self, requerimiento) -> bool:
        """Solo puede derivar si está asignado a él"""
        return self.puede_ver_requerimiento(requerimiento)

    def tiene_especialidad(self, especialidad: str) -> bool:
        """Verifica si el técnico tiene una especialidad específica"""
        return especialidad in self.especialidades

    def agregar_especialidad(self, especialidad: str) -> None:
        """Agrega una especialidad al técnico"""
        if especialidad not in self.especialidades:
            self.especialidades.append(especialidad)


class Supervisor(Usuario):
    """Supervisor que monitorea operadores y técnicos"""

    def __init__(
            self,
            id: Optional[int],
            nombre: str,
            email: Email,
            password_hash: str,
            operadores_supervisados: list[Operador] = None,
            tecnicos_supervisados: list[Tecnico] = None,
            fecha_creacion: Optional[datetime] = None,
            ultimo_acceso: Optional[datetime] = None
    ):
        super().__init__(id, nombre, email, password_hash, fecha_creacion, ultimo_acceso)
        self.operadores_supervisados = operadores_supervisados or []
        self.tecnicos_supervisados = tecnicos_supervisados or []
        self.notificaciones = []

    def get_tipo_usuario(self) -> TipoUsuario:
        return TipoUsuario.SUPERVISOR

    def puede_ver_requerimiento(self, requerimiento) -> bool:
        """Supervisores pueden ver todos los requerimientos"""
        return True

    def puede_comentar_requerimiento(self, requerimiento) -> bool:
        """Supervisores no comentan en requerimientos directamente"""
        return False

    def supervisa_operador(self, operador: Operador) -> bool:
        """Verifica si supervisa a un operador específico"""
        return operador in self.operadores_supervisados

    def supervisa_tecnico(self, tecnico: Tecnico) -> bool:
        """Verifica si supervisa a un técnico específico"""
        return tecnico in self.tecnicos_supervisados

    def supervisa_empleado(self, empleado: EmpleadoSoporte) -> bool:
        """Verifica si supervisa a un empleado (operador o técnico)"""
        if isinstance(empleado, Operador):
            return self.supervisa_operador(empleado)
        elif isinstance(empleado, Tecnico):
            return self.supervisa_tecnico(empleado)
        return False

    def agregar_operador_supervisado(self, operador: Operador) -> None:
        """Agrega un operador a la lista de supervisados"""
        if operador not in self.operadores_supervisados:
            self.operadores_supervisados.append(operador)

    def agregar_tecnico_supervisado(self, tecnico: Tecnico) -> None:
        """Agrega un técnico a la lista de supervisados"""
        if tecnico not in self.tecnicos_supervisados:
            self.tecnicos_supervisados.append(tecnico)

    def recibir_notificacion(self, notificacion) -> None:
        """Recibe una notificación"""
        self.notificaciones.append(notificacion)

    def get_notificaciones_no_leidas(self) -> list:
        """Retorna notificaciones no leídas"""
        return [n for n in self.notificaciones if not n.leida]