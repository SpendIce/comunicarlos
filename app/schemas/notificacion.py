from pydantic import BaseModel
from datetime import datetime

class NotificacionRead(BaseModel):
    id: int
    mensaje: str
    leida: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True