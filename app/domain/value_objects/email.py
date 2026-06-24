import re
from dataclasses import dataclass
from app.domain.exceptions import EmailInvalidoException


@dataclass(frozen=True)
class Email:
    """
    Value Object que encapsula la lógica de un correo electrónico.

    Concepto POO: Inmutabilidad. Al ser un Value Object, su identidad
    está definida por su valor, no por un ID. Usamos 'frozen=True' para
    evitar modificaciones accidentales post-creación.
    """
    valor: str

    def __post_init__(self):
        """Validación automática al instanciar el objeto."""
        if not self._es_formato_valido(self.valor):
            raise EmailInvalidoException(f"El formato del email '{self.valor}' no es válido.")

    @staticmethod
    def _es_formato_valido(email: str) -> bool:
        """Verifica el formato estándar de email usando Regex."""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(patron, email))

    def es_corporativo(self) -> bool:
        """
        Regla de Negocio: Verifica si el email pertenece al dominio de la organización.
        Requerido para Operadores y Técnicos.
        """
        return self.valor.endswith('@comunicarlos.com.ar')

    def __str__(self) -> str:
        return self.valor