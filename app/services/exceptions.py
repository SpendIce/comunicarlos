
class NotFoundException(Exception):
    """Recurso no encontrado"""
    pass

class UnauthorizedException(Exception):
    """Usuario no autorizado para la operación"""
    pass

class ConflictException(Exception):
    """Conflicto en el estado del recurso"""
    pass
