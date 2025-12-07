from fastapi import APIRouter, Depends
from app.schemas.reporte import DashboardOperadorResponse, DashboardTecnicoResponse
from app.dependencies.auth import verificar_rol_operador, verificar_rol_tecnico, get_current_user
from app.services.reporte_service import ReporteService
from app.dependencies.services import get_reporte_service

router = APIRouter()

@router.get("/dashboard-operador", response_model=DashboardOperadorResponse)
async def dashboard_operador(
    current_user = Depends(verificar_rol_operador),
    service: ReporteService = Depends(get_reporte_service)
):
    return await service.obtener_dashboard_operador()

@router.get("/dashboard-tecnico", response_model=DashboardTecnicoResponse)
async def dashboard_tecnico(
    current_user = Depends(verificar_rol_tecnico),
    service: ReporteService = Depends(get_reporte_service)
):
    return await service.obtener_dashboard_tecnico(current_user.id)