from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

      


""" ------- TOKEN ------- """
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str   

class MostrarToken(BaseModel):
    access_token: str
    token_type: str
    role: str
    usuario_id: int
    class Config:
        orm_mode = True

""" ------- ROL ------- """
class Rol(BaseModel):
    id: Optional[int] = None
    nombre: str 
    class Config:
        orm_mode = True   

""" ------- USUARIOS ------- """
class UsuarioLoginWithUsername(BaseModel):
    username: str
    password: str

class UsuarioLoginWithEmail(BaseModel):
    email: str
    password: str

class Usuario(BaseModel):
    id: Optional[int] = None
    username: str
    password: str
    email: Optional[str] = None
    rol_id: int = 3
    class Config:
        orm_mode = True

class UsuarioCreacion(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    rol_id: int = 3
    class Config:
        orm_mode = True

class UsuarioCambioContrasena(BaseModel):
    nueva_contrasena: str  
    class Config:
        orm_mode = True  

class MostrarUsuario(BaseModel):
    id: Optional[int] = None
    username: str
    email: Optional[str] = None
    rol: Rol  
    class Config:
        orm_mode = True

        

""" ------- DISPOSITIVOS ------- """
class Dispositivo(BaseModel):
    id: Optional[int] = None
    mac: Optional[str] = None
    nombre: Optional[str] = None
    active: Optional[bool] = None
    usuario_id: Optional[int] = None
    class Config:
        orm_mode = True

class MostrarDispositivo(BaseModel):
    id: Optional[int] = None
    mac: Optional[str] = None
    nombre: Optional[str] = None
    active: Optional[bool] = None
    usuario: MostrarUsuario
    class Config:
        orm_mode = True  

         

class MostrarDispositivoSinUsuario(BaseModel):
    id: Optional[int] = None
    mac: Optional[str] = None
    nombre: Optional[str] = None
    active: Optional[bool] = None
    class Config:
        orm_mode = True        

class CrearDispositivo(BaseModel):
    mac: str
    nombre: str
    active: Optional[bool] = None
    class Config:
        orm_mode = True          

class ActualizarDispositivo(BaseModel):
    mac: Optional[str] = None
    nombre: Optional[str] = None
    active: Optional[bool] = None
    usuario_id: Optional[int] = None
    class Config:
        orm_mode = True


""" ------- REGISTRO ------- """
class Registro(BaseModel):
    id: Optional[int] = None
    fecha: Optional[datetime] = None
    coordenadas: str
    class Config:
        orm_mode = True 

class MostrarRegistro(BaseModel):
    id: Optional[int] = None
    fecha: Optional[datetime] = None
    coordenadas: str
    dispositivo: Dispositivo 
    class Config:
        orm_mode = True  

class CrearRegistro(BaseModel):
    fecha: Optional[datetime] = None
    coordenadas: str
    mac: str
    class Config:
        orm_mode = True       




class MostrarDispositivoConRegistros(BaseModel):
    id: Optional[int] = None
    mac: Optional[str] = None
    nombre: Optional[str] = None
    active: Optional[bool] = None
    registros: list[Registro] = []
    class Config:
        orm_mode = True          