class NotFoundException(Exception):
    """Recurso no encontrado (HTTP 404)"""
    pass

class ConflictException(Exception):
    """Conflicto de estado, ej: email duplicado (HTTP 409)"""
    pass

class UnauthorizedException(Exception):
    """Fallo de autenticación (HTTP 401)"""
    pass

class PermissionDeniedException(Exception):
    """Fallo de autorización/roles (HTTP 403)"""
    pass

class BusinessRuleException(Exception):
    """Regla de negocio violada (HTTP 400/422)"""
    pass