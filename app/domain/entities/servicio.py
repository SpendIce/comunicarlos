from datetime import datetime
from typing import Optional
from app.domain.enums import TipoServicio
from app.domain.exceptions import ServicioException


class Servicio:
    """
    Producto o servicio contratado por un Solicitante.
    """

    def __init__(
            self,
            id: Optional[int],
            tipo: TipoServicio,
            numero_servicio: str,
            solicitante,  # Solicitante
            activo: bool = True,
            fecha_alta: Optional[datetime] = None
    ):
        self._validar_numero(numero_servicio)

        self.id = id
        self.tipo = tipo
        self.numero_servicio = numero_servicio
        self.solicitante = solicitante
        self._activo = activo  # Protegido, acceso vía propiedades/métodos
        self.fecha_alta = fecha_alta or datetime.now()

    def _validar_numero(self, numero: str):
        if len(numero) < 5:
            raise ServicioException("El número de servicio es inválido (muy corto).")

    # --- Encapsulamiento de Estado ---

    @property
    def activo(self) -> bool:
        """Propiedad de solo lectura pública."""
        return self._activo

    def activar(self) -> None:
        """Transición de estado controlada."""
        if self._activo:
            raise ServicioException("El servicio ya se encuentra activo.")
        self._activo = True

    def desactivar(self) -> None:
        """Transición de estado controlada."""
        if not self._activo:
            raise ServicioException("El servicio ya se encuentra inactivo.")
        self._activo = False

    def get_antiguedad_dias(self) -> int:
        """Calcula la antigüedad para reglas de prioridad (ej: Solicitudes)."""
        return (datetime.now() - self.fecha_alta).days

    def __str__(self) -> str:
        estado_str = "ACTIVO" if self._activo else "INACTIVO"
        return f"{self.tipo.value} [{self.numero_servicio}] - {estado_str}"