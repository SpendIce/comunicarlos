from datetime import datetime
from typing import Optional


class Comentario:
    """Comentario en un requerimiento - Inmutable después de creado"""

    def __init__(
            self,
            id: Optional[int],
            texto: str,
            autor,  # Usuario
            requerimiento,  # Requerimiento
            fecha_hora: Optional[datetime] = None
    ):
        self.id = id
        self._texto = texto
        self._autor = autor
        self._requerimiento = requerimiento
        self._fecha_hora = fecha_hora or datetime.now()

        # Validaciones
        if len(texto.strip()) < 5:
            raise ValueError("El comentario debe tener al menos 5 caracteres")

    @property
    def texto(self) -> str:
        """Comentario es inmutable"""
        return self._texto

    @property
    def autor(self):
        """Autor es inmutable"""
        return self._autor

    @property
    def requerimiento(self):
        """Requerimiento es inmutable"""
        return self._requerimiento

    @property
    def fecha_hora(self) -> datetime:
        """Fecha es inmutable"""
        return self._fecha_hora

    def __str__(self) -> str:
        return f"{self.autor.nombre}: {self.texto[:50]}..."

    def __repr__(self) -> str:
        return f"<Comentario(id={self.id}, autor='{self.autor.nombre}', fecha='{self.fecha_hora}')>"
