from typing import Optional
from app.domain.entities.usuario import Usuario
from app.domain.exceptions import CredencialesInvalidasException


# Asumimos que existen interfaces de repositorio (Duck Typing o ABCs)
# from app.repositories.usuario_repository import UsuarioRepository

class AuthenticationService:
    """
    Servicio encargado de la seguridad y control de acceso.

    Responsabilidad:
    Actúa como la puerta de entrada. Verifica 'quién eres' (Autenticación)
    para que las otras capas puedan verificar 'qué puedes hacer' (Autorización).
    """

    def __init__(self, usuario_repository, hash_provider):
        # Inyección de Dependencias: Facilita el testing mockeando el repo o el hasher
        self.usuario_repository = usuario_repository
        self.hash_provider = hash_provider

    def autenticar(self, email: str, password_plana: str) -> Usuario:
        """
        Verifica las credenciales del usuario.

        Flujo:
        1. Busca al usuario por email.
        2. Si existe, verifica el hash de la contraseña.
        3. Si es correcto, actualiza su último acceso (Auditabilidad).
        4. Retorna la entidad Usuario hidrata (Solicitante, Tecnico, etc.).
        """
        usuario = self.usuario_repository.buscar_por_email(email)

        if not usuario:
            # Por seguridad, no especificamos si falló el email o el pass
            raise CredencialesInvalidasException("Credenciales incorrectas")

        if not self.hash_provider.verificar(password_plana, usuario.password_hash):
            raise CredencialesInvalidasException("Credenciales incorrectas")

        # Regla de Negocio: Auditabilidad de accesos (Requerido por PDF)
        usuario.actualizar_ultimo_acceso()
        self.usuario_repository.actualizar(usuario)

        return usuario


AutenticacionService = AuthenticationService
