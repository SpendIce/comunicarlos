from fastapi import APIRouter, Path, Query, Depends, status
from typing import List
from app.schemas.comentario import CrearComentarioRequest, ComentarioResponse, ListaComentariosResponse
from app.dependencies.auth import get_current_user
from app.services.comentario_service import ComentarioService
from app.dependencies.services import get_comentario_service

router = APIRouter()

@router.post("/{id}/comentarios", response_model=ComentarioResponse, status_code=status.HTTP_201_CREATED)
async def agregar_comentario(
        id: int = Path(...),
        request: CrearComentarioRequest = None,
        current_user=Depends(get_current_user),
        service: ComentarioService = Depends(get_comentario_service)
):
    return await service.agregar_comentario(
        requerimiento_id=id,
        usuario_id=current_user.id,
        texto=request.texto
    )


@router.get("/{id}/comentarios", response_model=ListaComentariosResponse)
async def listar_comentarios(
        id: int = Path(...),
        orden: str = Query("asc"),
        current_user=Depends(get_current_user),
        service: ComentarioService = Depends(get_comentario_service)
):
    comentarios = await service.listar_comentarios(id, current_user)
    if orden == "desc":
        comentarios.reverse()

    return {
        "requerimientoId": id,
        "comentarios": comentarios,
        "totalComentarios": len(comentarios)
    }