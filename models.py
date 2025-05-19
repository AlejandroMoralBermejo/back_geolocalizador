from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional


class UsuarioLogin(BaseModel):
    username: str
    password: str

class Usuario(BaseModel):
    id: Optional[int] = None
    username: str
    password: str
    email: Optional[str] = None
    rol_id: int = 3

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

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

class Rol(BaseModel):
    id: Optional[int] = None
    nombre: str    

class UsuarioCambioContrasena(BaseModel):
    nueva_contrasena: str    