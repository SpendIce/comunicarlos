from datetime import datetime
from typing import Optional
from app.domain.enums import TipoServicio
from app.domain.exceptions import ServicioException


class Servicio:
    """Servicio suscrito por un solicitante"""

    def __init__(
            self,
            id: Optional[int],
            tipo: TipoServicio,
            numero_servicio: str,
            solicitante,  # Solicitante
            activo: bool = True,
            fecha_alta: Optional[datetime] = None
    ):
        self.id = id
        self.tipo = tipo
        self.numero_servicio = numero_servicio
        self.solicitante = solicitante
        self.activo = activo
        self.fecha_alta = fecha_alta or datetime.now()

        # Validaciones
        if len(numero_servicio) < 5:
            raise ServicioException("El número de servicio debe tener al menos 5 caracteres")

    def activar(self) -> None:
        """Activa el servicio"""
        if self.activo:
            raise ServicioException("El servicio ya está activo")
        self.activo = True

    def desactivar(self) -> None:
        """Desactiva el servicio"""
        if not self.activo:
            raise ServicioException("El servicio ya está inactivo")
        self.activo = False

    def esta_activo(self) -> bool:
        """Verifica si el servicio está activo"""
        return self.activo

    def get_dias_desde_alta(self) -> int:
        """Calcula los días desde que fue dado de alta"""
        delta = datetime.now() - self.fecha_alta
        return delta.days

    def __str__(self) -> str:
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.tipo.value} ({self.numero_servicio}) - {estado}"

    def __repr__(self) -> str:
        return f"<Servicio(id={self.id}, tipo='{self.tipo.value}', activo={self.activo})>"
