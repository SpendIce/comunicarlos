from app.repositories.requerimiento_repository import RequerimientoRepository
from app.repositories.usuario_repository import UsuarioRepository
from datetime import datetime
from app.domain.enums import TipoEvento


class ReporteService:
    def __init__(self, req_repo: RequerimientoRepository, user_repo: UsuarioRepository):
        self.req_repo = req_repo
        self.user_repo = user_repo

    async def obtener_dashboard_operador(self):
        dist_estado = await self.req_repo.obtener_distribucion_estado()
        dist_urgencia = await self.req_repo.obtener_distribucion_urgencia()
        criticos = await self.req_repo.obtener_incidentes_criticos_pendientes()
        tecnicos = await self.user_repo.buscar_tecnicos()
        tecnicos_stats = []
        for tec in tecnicos:
            asignados = await self.req_repo.collection.count_documents({
                "tecnico_asignado_id": tec.id,
                "estado": "ASIGNADO"
            })
            en_proceso = await self.req_repo.collection.count_documents({
                "tecnico_asignado_id": tec.id,
                "estado": "EN_PROCESO"
            })

            total_activos = asignados + en_proceso

            tecnicos_stats.append({
                "tecnico": {
                    "id": tec.id,
                    "nombre": tec.nombre,
                    "email": str(tec.email)
                },
                "requerimientosAsignados": asignados,
                "requerimientosEnProceso": en_proceso,
                "disponibilidad": "ALTA" if total_activos < 3 else "MEDIA" if total_activos < 5 else "BAJA"
            })
        # Mapeo a objeto de respuesta
        return {
            "resumen": {
                "requerimientosNuevos": dist_estado.get("NUEVO", 0),
                "requerimientosSinAsignar": dist_estado.get("NUEVO", 0),  # Asumiendo NUEVO = Sin Asignar
                "incidentesCriticos": sum(1 for c in criticos)
            },
            "distribucionPorEstado": dist_estado,
            "distribucionPorUrgencia": dist_urgencia,
            "tecnicosDisponibilidad": tecnicos_stats,
            "requerimientosPrioritarios": [
                {
                    "id": c["_id"],
                    "titulo": c["titulo"],
                    "urgencia": "CRITICO",
                    "prioridad": 100,
                    "diasDesdeCreacion": (datetime.now() - c["fecha_creacion"]).days
                } for c in criticos
            ]
        }

    async def obtener_dashboard_tecnico(self, tecnico_id: int):
        tecnico = await self.user_repo.buscar_por_id(tecnico_id)
        total_resueltos = await self.req_repo.collection.count_documents(
            {"tecnico_asignado_id": tecnico_id, "estado": "RESUELTO"})

        asignados = await self.req_repo.collection.count_documents(
            {"tecnico_asignado_id": tecnico_id})

        en_proceso = await self.req_repo.collection.count_documents(
            {"tecnico_asignado_id": tecnico_id, "estado": "EN_PROCESO"})

        pendientes_docs, _ = await self.req_repo.buscar_con_filtros(
            {"tecnico_asignado_id": tecnico_id, "estado": {"$ne": "RESUELTO"}}, 0, 10)

        interconsultas = []
        for req in pendientes_docs:
            if req.eventos:
                ultimo_evento = req.eventos[-1]
                if ultimo_evento.get_tipo_evento() == TipoEvento.DERIVACION:
                    interconsultas.append({
                        "id": req.id,
                        "titulo": req.titulo,
                        "origen": ultimo_evento.tecnico_origen.nombre if hasattr(ultimo_evento,
                                                                                 'tecnico_origen') else "Desconocido",
                        "motivo": ultimo_evento.motivo if hasattr(ultimo_evento, 'motivo') else ""
                    })

        return {
            "tecnico": {
                "id": tecnico_id,
                "nombre": tecnico.nombre if tecnico else "Tecnico",
                "email": str(tecnico.email) if tecnico else ""
            },
            "resumen": {
                "requerimientosAsignados": asignados,
                "requerimientosEnProceso": en_proceso,
                "requerimientosResueltos": total_resueltos,
                "promedioTiempoResolucion": "4 horas"
            },
            "misRequerimientos": [
                {
                    "id": r.id,
                    "titulo": r.titulo,
                    "estado": r.estado.value,
                    "urgencia": getattr(r, 'nivel_urgencia', None),
                    "prioridad": r.calcular_prioridad(),
                    "diasDesdeCreacion": r.get_dias_desde_creacion(),
                    "ultimaActividad": r.eventos[-1].fecha_hora if r.eventos else r.fecha_creacion
                } for r in pendientes_docs
            ],
            "interconsultas": interconsultas
        }