from enum import Enum


class TipoUsuario(str, Enum):
    SOLICITANTE = "SOLICITANTE"
    OPERADOR = "OPERADOR"
    TECNICO = "TECNICO"
    SUPERVISOR = "SUPERVISOR"


class TipoRequerimiento(str, Enum):
    INCIDENTE = "INCIDENTE"
    SOLICITUD = "SOLICITUD"


class EstadoRequerimiento(str, Enum):
    NUEVO = "NUEVO"
    ASIGNADO = "ASIGNADO"
    EN_PROCESO = "EN_PROCESO"
    RESUELTO = "RESUELTO"
    REABIERTO = "REABIERTO"


class NivelUrgencia(str, Enum):
    CRITICO = "CRITICO"
    IMPORTANTE = "IMPORTANTE"
    MENOR = "MENOR"

    def get_peso(self) -> int:
        """Retorna el peso numérico para cálculo de prioridad"""
        pesos = {
            NivelUrgencia.CRITICO: 100,
            NivelUrgencia.IMPORTANTE: 50,
            NivelUrgencia.MENOR: 10
        }
        return pesos[self]


class CategoriaIncidente(str, Enum):
    SERVICIO_INACCESIBLE = "SERVICIO_INACCESIBLE"
    BLOQUEO_SIM = "BLOQUEO_SIM"
    PERDIDA_DESTRUCCION_EQUIPOS = "PERDIDA_DESTRUCCION_EQUIPOS"


class CategoriaSolicitud(str, Enum):
    ALTA_SERVICIO = "ALTA_SERVICIO"
    BAJA_SERVICIO = "BAJA_SERVICIO"


class TipoServicio(str, Enum):
    TELEFONIA_CELULAR = "TELEFONIA_CELULAR"
    INTERNET_BANDA_ANCHA = "INTERNET_BANDA_ANCHA"
    TELEVISION = "TELEVISION"


class TipoEvento(str, Enum):
    CREACION = "CREACION"
    ASIGNACION = "ASIGNACION"
    DERIVACION = "DERIVACION"
    RESOLUCION = "RESOLUCION"
    REAPERTURA = "REAPERTURA"
    COMENTARIO = "COMENTARIO"