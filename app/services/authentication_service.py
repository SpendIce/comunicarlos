import hashlib
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.domain import (
    Usuario, Solicitante, Operador, Tecnico, Supervisor, Email, Servicio
)
from app.domain.enums import TipoUsuario, TipoServicio
from app.services.exceptions import UnauthorizedException, NotFoundException, ConflictException
from app.config import settings

# Configuración de encriptación de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AutenticacionService:
    """
    Servicio de autenticación y gestión de usuarios.
    Maneja registro, login, validación de tokens JWT.
    """

    def __init__(self, usuario_repository, servicio_repository):
        """
        Args:
            usuario_repository: Repositorio de usuarios
            servicio_repository: Repositorio de servicios
        """
        self.usuario_repo = usuario_repository
        self.servicio_repo = servicio_repository

    # ========================================================================
    # Gestión de Passwords
    # ========================================================================

    def _pre_hash_password(self, password: str) -> str:
        """
        Convierte la contraseña a un hash SHA-256 intermedio.
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def hash_password(self, password: str) -> str:
        """
        Genera hash de password usando SHA-256 + bcrypt.
        """
        password_pre_hashed = self._pre_hash_password(password)
        return pwd_context.hash(password_pre_hashed)

    def verificar_password(self, password_plano: str, password_hash: str) -> bool:
        """
        Verifica si un password coincide con su hash.
        """
        try:
            password_pre_hashed = self._pre_hash_password(password_plano)
            return pwd_context.verify(password_pre_hashed, password_hash)
        except Exception:
            return False

    # ========================================================================
    # JWT
    # ========================================================================

    def crear_token_acceso(self, usuario: Usuario) -> str:
        """
        Crea un token JWT para el usuario.

        Args:
            usuario: Usuario autenticado

        Returns:
            str: Token JWT
        """
        expiracion = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload = {
            "sub": str(usuario.id),
            "email": str(usuario.email),
            "tipo_usuario": usuario.get_tipo_usuario().value,
            "exp": expiracion
        }

        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return token

    def validar_token(self, token: str) -> dict:
        """
        Valida y decodifica un token JWT.

        Args:
            token: Token JWT

        Returns:
            dict: Payload del token

        Raises:
            UnauthorizedException: Si el token es inválido
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError as e:
            raise UnauthorizedException(f"Token inválido: {str(e)}")

    def obtener_usuario_desde_token(self, token: str) -> Usuario:
        """
        Obtiene el usuario asociado a un token JWT.

        Args:
            token: Token JWT

        Returns:
            Usuario: Usuario autenticado

        Raises:
            UnauthorizedException: Si el token es inválido
            NotFoundException: Si el usuario no existe
        """
        payload = self.validar_token(token)
        user_id = int(payload.get("sub"))

        usuario = self.usuario_repo.buscar_por_id(user_id)
        if not usuario:
            raise NotFoundException(f"Usuario con ID {user_id} no encontrado")

        return usuario

    # ========================================================================
    # Registro y Login
    # ========================================================================

    async def registrar_usuario(
            self,
            nombre: str,
            email: str,
            password: str,
            tipo_usuario: TipoUsuario,
            servicios_suscritos: list = None
    ) -> Usuario:
        """
        Registra un nuevo usuario en el sistema.

        Args:
            nombre: Nombre completo
            email: Email (corporativo para empleados)
            password: Password en texto plano
            tipo_usuario: Tipo de usuario (SOLICITANTE, OPERADOR, etc.)
            servicios_suscritos: Lista de servicios (solo para solicitantes)

        Returns:
            Usuario: Usuario creado

        Raises:
            ServiceException: Si hay errores de validación
        """
        # Validar que el email no exista
        if await self.usuario_repo.existe_email(email):
            raise ConflictException(f"El email {email} ya está registrado")

        # Crear value object Email (auto-valida formato)
        email_vo = Email(email)

        # Hash del password
        password_hash = self.hash_password(password)

        # Crear usuario según tipo
        if tipo_usuario == TipoUsuario.SOLICITANTE:
            if not servicios_suscritos:
                raise ValueError("Los solicitantes deben tener al menos un servicio")

            usuario = Solicitante(
                id=None,
                nombre=nombre,
                email=email_vo,
                password_hash=password_hash
            )

            # Crear servicios
            for servicio_data in servicios_suscritos:
                servicio = Servicio(
                    id=None,
                    tipo=TipoServicio[servicio_data["tipo"]],
                    numero_servicio=servicio_data["numeroServicio"],
                    solicitante=usuario,
                    activo=True
                )
                usuario.agregar_servicio(servicio)

        elif tipo_usuario == TipoUsuario.OPERADOR:
            usuario = Operador(
                id=None,
                nombre=nombre,
                email=email_vo,
                password_hash=password_hash
            )

        elif tipo_usuario == TipoUsuario.TECNICO:
            usuario = Tecnico(
                id=None,
                nombre=nombre,
                email=email_vo,
                password_hash=password_hash,
                especialidades=[]
            )

        elif tipo_usuario == TipoUsuario.SUPERVISOR:
            usuario = Supervisor(
                id=None,
                nombre=nombre,
                email=email_vo,
                password_hash=password_hash
            )

        else:
            raise ValueError(f"Tipo de usuario inválido: {tipo_usuario}")

        # Guardar en repositorio
        usuario_guardado = await self.usuario_repo.guardar(usuario)
        return usuario_guardado

    async def autenticar(self, email: str, password: str) -> tuple[Usuario, str]:
        """
        Autentica un usuario y genera token JWT.

        Args:
            email: Email del usuario
            password: Password en texto plano

        Returns:
            tuple: (Usuario, token_jwt)

        Raises:
            UnauthorizedException: Si las credenciales son inválidas
        """
        # Buscar usuario por email
        usuario = await self.usuario_repo.buscar_por_email(email)
        if not usuario:
            raise UnauthorizedException("Credenciales inválidas")

        # Verificar password
        if not self.verificar_password(password, usuario.password_hash):
            raise UnauthorizedException("Credenciales inválidas")

        # Actualizar último acceso
        usuario.actualizar_ultimo_acceso()
        await self.usuario_repo.guardar(usuario)

        # Generar token
        token = self.crear_token_acceso(usuario)
        return usuario, token