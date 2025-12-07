import re
from dataclasses import dataclass
from app.domain.exceptions import EmailInvalidoException


@dataclass(frozen=True)
class Email:
    """Value Object para emails - Inmutable"""
    valor: str

    def __post_init__(self):
        if not self._es_valido(self.valor):
            raise EmailInvalidoException(f"Email inválido: {self.valor}")

    @staticmethod
    def _es_valido(email: str) -> bool:
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(patron, email))

    def es_corporativo(self) -> bool:
        """Verifica si es email corporativo @comunicarlos.com.ar"""
        return self.valor.endswith('@comunicarlos.com.ar')

    def __str__(self) -> str:
        return self.valor