from app.repositories.requerimiento_repository import RequerimientoRepository
from app.repositories.usuario_repository import UsuarioRepository
from datetime import datetime


class ReporteService:
    def __init__(self, req_repo: RequerimientoRepository, user_repo: UsuarioRepository):
        self.req_repo = req_repo
        self.user_repo = user_repo

    async def obtener_dashboard_operador(self):
        dist_estado = await self.req_repo.obtener_distribucion_estado()
        dist_urgencia = await self.req_repo.obtener_distribucion_urgencia()
        criticos = await self.req_repo.obtener_incidentes_criticos_pendientes()

        # Mapeo a objeto de respuesta
        return {
            "resumen": {
                "requerimientosNuevos": dist_estado.get("NUEVO", 0),
                "requerimientosSinAsignar": dist_estado.get("NUEVO", 0),  # Asumiendo NUEVO = Sin Asignar
                "incidentesCriticos": sum(1 for c in criticos),
                "promedioTiempoAsignacion": "2.5 horas"  # Placeholder: requeriría cálculo complejo de logs
            },
            "distribucionPorEstado": dist_estado,
            "distribucionPorUrgencia": dist_urgencia,
            "tecnicosDisponibilidad": [],  # Implementar lógica de carga de técnicos
            "requerimientosPrioritarios": [
                {
                    "id": c["_id"],
                    "titulo": c["titulo"],
                    "urgencia": "CRITICO",
                    "prioridad": 100,  # Simplificado
                    "diasDesdeCreacion": (datetime.now() - c["fecha_creacion"]).days
                } for c in criticos
            ]
        }

    async def obtener_dashboard_tecnico(self, tecnico_id: int):
        # Lógica específica para técnico
        metricas = await self.req_repo.collection.count_documents(
            {"tecnico_asignado_id": tecnico_id, "estado": "RESUELTO"})
        pendientes = await self.req_repo.buscar_con_filtros(
            {"tecnico_asignado_id": tecnico_id, "estado": {"$ne": "RESUELTO"}}, 0, 10)

        return {
            "tecnico": {"id": tecnico_id, "nombre": "Actual", "email": ""},  # Se completaría con datos reales
            "resumen": {
                "requerimientosAsignados": await self.req_repo.collection.count_documents(
                    {"tecnico_asignado_id": tecnico_id}),
                "requerimientosEnProceso": await self.req_repo.collection.count_documents(
                    {"tecnico_asignado_id": tecnico_id, "estado": "EN_PROCESO"}),
                "requerimientosResueltos": metricas,
                "promedioTiempoResolucion": "4 horas"
            },
            "misRequerimientos": [
                {
                    "id": r.id,
                    "titulo": r.titulo,
                    "estado": r.estado.value,
                    "urgencia": r.nivel_urgencia.value if hasattr(r, 'nivel_urgencia') else None,
                    "prioridad": r.calcular_prioridad(),
                    "diasDesdeCreacion": r.get_dias_desde_creacion(),
                    "ultimaActividad": r.eventos[-1].fecha_hora if r.eventos else r.fecha_creacion
                } for r in pendientes[0]
            ],
            "interconsultas": []
        }