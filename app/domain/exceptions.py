class RequerimientoException(Exception):
    """Excepciones relacionadas con requerimientos"""
    pass

class EstadoInvalidoException(RequerimientoException):
    """El estado del requerimiento no permite la operación"""
    pass

class PermisosDenegadosException(Exception):
    """El usuario no tiene permisos para realizar la acción"""
    pass

class ValidacionException(Exception):
    """Errores de validación de datos"""
    pass

class UsuarioException(Exception):
    """Excepciones relacionadas con usuarios"""
    pass

class EmailInvalidoException(UsuarioException):
    """Email no válido según las reglas del dominio"""
    pass

class ServicioException(Exception):
    """Excepciones relacionadas con servicios"""
    pass
