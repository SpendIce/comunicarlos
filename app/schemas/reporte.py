from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ResumenOperador(BaseModel):
    requerimientosNuevos: int
    requerimientosSinAsignar: int
    incidentesCriticos: int
    promedioTiempoAsignacion: str

class DistribucionEstado(BaseModel):
    NUEVO: int = 0
    ASIGNADO: int = 0
    EN_PROCESO: int = 0
    RESUELTO: int = 0
    REABIERTO: int = 0

class DistribucionUrgencia(BaseModel):
    CRITICO: int = 0
    IMPORTANTE: int = 0
    MENOR: int = 0

class TecnicoDisponibilidad(BaseModel):
    tecnico: Dict
    requerimientosAsignados: int
    requerimientosEnProceso: int
    disponibilidad: str

class RequerimientoPrioritario(BaseModel):
    id: int
    titulo: str
    urgencia: Optional[str]
    prioridad: int
    diasDesdeCreacion: int

class DashboardOperadorResponse(BaseModel):
    resumen: ResumenOperador
    distribucionPorEstado: DistribucionEstado
    distribucionPorUrgencia: DistribucionUrgencia
    tecnicosDisponibilidad: List[TecnicoDisponibilidad]
    requerimientosPrioritarios: List[RequerimientoPrioritario]

class ResumenTecnico(BaseModel):
    requerimientosAsignados: int
    requerimientosEnProceso: int
    requerimientosResueltos: int
    promedioTiempoResolucion: str
    satisfaccionPromedio: Optional[float] = None

class MiRequerimiento(BaseModel):
    id: int
    titulo: str
    urgencia: Optional[str]
    estado: str
    prioridad: int
    diasDesdeCreacion: int
    ultimaActividad: datetime

class Interconsulta(BaseModel):
    id: int
    titulo: str
    tecnicoOrigen: str
    fechaDerivacion: datetime
    motivo: str

class DashboardTecnicoResponse(BaseModel):
    tecnico: Dict
    resumen: ResumenTecnico
    misRequerimientos: List[MiRequerimiento]
    interconsultas: List[Interconsulta]

class MetricasSupervisor(BaseModel):
    requerimientosGestionados: int
    requerimientosResueltos: int
    tasaResolucion: float
    tiempoPromedioResolucion: str
    notificacionesPendientes: int

class RendimientoOperador(BaseModel):
    operador: Dict
    requerimientosAsignados: int
    tiempoPromedioAsignacion: str
    eficienciaAsignacion: float

class RendimientoTecnico(BaseModel):
    tecnico: Dict
    requerimientosResueltos: int
    tiempoPromedioResolucion: str
    tasaResolucion: float
    requerimientosReabiertos: int

class IncidenteCriticoInfo(BaseModel):
    id: int
    titulo: str
    tecnicoAsignado: Optional[str]
    diasDesdeCreacion: int
    ultimaActividad: datetime

class DashboardSupervisorResponse(BaseModel):
    supervisor: Dict
    metricas: MetricasSupervisor
    rendimientoOperadores: List[RendimientoOperador]
    rendimientoTecnicos: List[RendimientoTecnico]
    incidentesCriticosSinResolver: List[IncidenteCriticoInfo]

class EventoHistorial(BaseModel):
    fechaHora: datetime
    tipo: str
    actor: str
    descripcion: str
    texto: Optional[str] = None
    detalles: Optional[Dict] = None

class EstadisticasHistorial(BaseModel):
    tiempoTotal: str
    tiempoHastaAsignacion: str
    tiempoResolucion: str
    totalComentarios: int
    totalEventos: int

class HistorialRequerimientoResponse(BaseModel):
    requerimiento: Dict
    linea_tiempo: List[EventoHistorial]
    estadisticas: EstadisticasHistorial

class PeriodoReporte(BaseModel):
    desde: datetime
    hasta: datetime

class RequerimientosStats(BaseModel):
    total: int
    incidentes: int
    solicitudes: int
    resueltos: int
    pendientes: int
    tasaResolucion: float

class TiemposStats(BaseModel):
    promedioAsignacion: str
    promedioResolucion: str
    promedioRespuesta: str

class UrgenciasStats(BaseModel):
    criticos: int
    importantes: int
    menores: int

class CategoriaStats(BaseModel):
    categoria: str
    cantidad: int
    porcentaje: float

class UsuariosStats(BaseModel):
    solicitantes: int
    operadores: int
    tecnicos: int
    supervisores: int

class EstadisticasGlobalesResponse(BaseModel):
    periodo: PeriodoReporte
    requerimientos: RequerimientosStats
    tiempos: TiemposStats
    urgencias: UrgenciasStats
    categorias: List[CategoriaStats]
    usuarios: UsuariosStats