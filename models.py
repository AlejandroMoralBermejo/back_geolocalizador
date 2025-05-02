from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional


class Usuario(BaseModel):
    id: Optional[int] = None
    username: str
    password: str
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class Dispositivo(BaseModel):
    id: Optional[int] = None
    nombre: Optional[str] = None
    active: Optional[bool] = None
    usuario_id: Optional[int] = None


class Registro(BaseModel):
    id: Optional[int] = None
    fecha: Optional[datetime] = None
    coordenadas: str
    dispositivo_id: int