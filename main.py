from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from database import SessionLocal, UsuarioDB, DispositivoDB, RegistroDB, RolDB
from models import Usuario, Dispositivo, Registro, Token, Rol
from uuid import uuid4
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
import datetime
import re
from dotenv import load_dotenv
import os

app = FastAPI()

ruta_inicial = "/api/v1.5/"

# Middleware CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

# Configuración del hash bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''--------------------- AUTENTICACIÓN ---------------------'''
def hash_password(password: str) -> str:
    """ Hashea la contraseña usando bcrypt """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ Verifica si la contraseña en texto plano coincide con el hash almacenado """
    return pwd_context.verify(plain_password, hashed_password)

# Función para crear el token de acceso JWT
def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para verificar el token JWT
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Función para obtener el usuario actual desde el token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(UsuarioDB).filter(UsuarioDB.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post(ruta_inicial + "token", response_model=Token)
def login_for_access_token(form_data: Usuario, db: Session = Depends(get_db)):
    """ Endpoint para obtener el token de acceso al enviar el username y password """
    user = db.query(UsuarioDB).filter(UsuarioDB.username == form_data.username).first()

    # Verificar si el usuario existe y la contraseña es válida
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.username, "role": user.rol.nombre}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.rol.nombre
    }

'''--------------------- USUARIOS ---------------------'''

@app.get(ruta_inicial + "usuarios/", response_model=List[Usuario])
def obtener_usuarios(db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    return db.query(UsuarioDB).all()

@app.post(ruta_inicial + "usuarios/", response_model=Usuario)
def crear_usuario(usuario: Usuario, db: Session = Depends(get_db)):
    """ Crea un nuevo usuario con la contraseña hasheada """
    hashed_password = hash_password(usuario.password)  # Hasheamos la contraseña
    nuevo_usuario = UsuarioDB(username=usuario.username, password=hashed_password, email=usuario.email, rol_id=usuario.rol_id)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@app.get(ruta_inicial + "usuarios/{usuario_id}", response_model=Usuario)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@app.delete(ruta_inicial + "usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db),current_user: UsuarioDB = Depends(get_current_user)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return {"message": "Usuario eliminado"}

'''--------------------- DISPOSITIVOS ---------------------'''
@app.get(ruta_inicial + "dispositivos/", response_model=List[Dispositivo])
def obtener_dispositivos(db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    return db.query(DispositivoDB).all()

@app.post(ruta_inicial + "dispositivos/", response_model=Dispositivo)
def crear_dispositivo(dispositivo: Dispositivo, db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    usuario_existente = db.query(UsuarioDB).filter(UsuarioDB.id == dispositivo.usuario_id).first()

    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    nuevo_dispositivo = DispositivoDB(active=dispositivo.active, nombre=dispositivo.nombre, usuario_id=dispositivo.usuario_id)
    db.add(nuevo_dispositivo)
    db.commit()
    db.refresh(nuevo_dispositivo)
    return nuevo_dispositivo

# Obtener dispositivo por id
@app.get(ruta_inicial + "dispositivos/{dispositivo_id}", response_model=Dispositivo)
def obtener_dispositivo(dispositivo_id: int, db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    dispositivo = db.query(DispositivoDB).filter(DispositivoDB.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dispositivo

@app.get(ruta_inicial + "dispositivos/usuario/{usuario_id}", response_model=List[Dispositivo])
def obtener_dispositivo_por_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    dispositivos = db.query(DispositivoDB).filter(DispositivoDB.usuario_id == usuario_id).all()
    if not dispositivos:
        raise HTTPException(status_code=404, detail="No se encontraron dispositivos para este usuario")
    return dispositivos

@app.delete(ruta_inicial + "dispositivos/{dispositivo_id}")
def eliminar_dispositivo(dispositivo_id: int, db: Session = Depends(get_db),current_user: UsuarioDB = Depends(get_current_user)):
    dispositivo = db.query(DispositivoDB).filter(DispositivoDB.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    db.delete(dispositivo)
    db.commit()
    return {"message": "Dispositivo eliminado"}

@app.patch(ruta_inicial + "dispositivos/{dispositivo_id}", response_model=Dispositivo)
def actualizar_dispositivo(dispositivo_id: int, dispositivo: Dispositivo, db: Session = Depends(get_db),current_user: UsuarioDB = Depends(get_current_user)):
    dispositivo_existente = db.query(DispositivoDB).filter(DispositivoDB.id == dispositivo_id).first()
    if not dispositivo_existente:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    if(dispositivo.nombre is not None):
        dispositivo_existente.nombre = dispositivo.nombre
    
    if(dispositivo.active is not None):    
        dispositivo_existente.active = dispositivo.active

    db.commit()
    db.refresh(dispositivo_existente)
    return dispositivo_existente


'''--------------------- ROLES ---------------------'''
@app.get(ruta_inicial + "roles/", response_model=List[Rol])
def obtener_roles(db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    return db.query(RolDB).all()

'''--------------------- REGISTROS ---------------------'''
@app.get(ruta_inicial + "registros/", response_model=List[Registro])
def obtener_registros(db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    return db.query(RegistroDB).all()


# Funcion para formatear la fecha
def formateo(datos_gnss):
    try:
        print(f"Datos GNSS recibidos: {datos_gnss}")  # Debugging

        # Eliminar el prefijo "+CGPSINFO:" si está presente
        datos_gnss = re.sub(r"^\+CGPSINFO:\s*", "", datos_gnss)

        partes = datos_gnss.split(',')[:4]  # Solo tomamos las primeras 4 partes (lat, N/S, lon, E/W)

        if len(partes) < 4:
            raise ValueError("Formato de datos GNSS incorrecto.")

        lat_dmm, ns, lon_dmm, ew = map(str.strip, partes)

        # Convertir latitud
        lat_grados = int(lat_dmm[:2])
        lat_minutos = float(lat_dmm[2:]) / 60
        lat_decimal = lat_grados + lat_minutos
        if ns == 'S':
            lat_decimal *= -1

        # Convertir longitud
        lon_grados = int(lon_dmm[:3])
        lon_minutos = float(lon_dmm[3:]) / 60
        lon_decimal = lon_grados + lon_minutos
        if ew == 'W':
            lon_decimal *= -1

        coordenadas = f"{lat_decimal},{lon_decimal}"

        print(f"Coordenadas convertidas: {coordenadas}")  # Debugging
        return coordenadas

    except Exception as e:
        print("Fallo en el formateo:", e)
        return None


@app.post(ruta_inicial + "registros/", response_model=Registro)
def crear_registro(registro: Registro, db: Session = Depends(get_db)):
    dispositivo_existente = db.query(DispositivoDB).filter(DispositivoDB.id == registro.dispositivo_id).first()
    if not dispositivo_existente:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    if not registro.coordenadas:
        raise HTTPException(status_code=400, detail="Datos GNSS no proporcionados")

    # Llamamos a la función formateo para obtener las coordenadas
    coordenadas = formateo(registro.coordenadas)

    if coordenadas is None:
        raise HTTPException(status_code=400, detail="Datos GNSS inválidos o no disponibles")

    nuevo_registro = RegistroDB(
        coordenadas=coordenadas,  # Solo almacenamos las coordenadas
        dispositivo_id=registro.dispositivo_id
    )

    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return nuevo_registro

