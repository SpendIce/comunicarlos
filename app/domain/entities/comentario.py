from datetime import datetime
from typing import Optional
from app.domain.exceptions import ValidacionException


class Comentario:
    """
    Representa una interacción textual dentro de un requerimiento.

    Regla de Negocio:
    - Inmutabilidad: No tiene setters. Lo dicho, dicho está (Auditabilidad).
    - Preserva la identidad del autor y el momento exacto.
    """

    def __init__(
            self,
            id: Optional[int],
            contenido: Optional[str] = None,
            autor=None,  # Usuario
            requerimiento=None,
            fecha_hora: Optional[datetime] = None,
            texto: Optional[str] = None
    ):
        contenido = texto if texto is not None else contenido
        if not contenido or len(contenido.strip()) == 0:
            raise ValidacionException("No se puede registrar un comentario vacío.")

        self.id = id
        self.contenido = contenido
        self.texto = contenido
        self.autor = autor
        self.requerimiento = requerimiento
        self.fecha_hora = fecha_hora or datetime.now()

    def __str__(self) -> str:
        return f"{self.autor.nombre} ({self.fecha_hora}): {self.texto[:20]}..."

    def __repr__(self) -> str:
        return f"<Comentario(id={self.id}, autor='{self.autor.email}')>"
