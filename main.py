import datetime
import re
import os
from database import SessionLocal, UsuarioDB, DispositivoDB, RegistroDB, RolDB
import models
from uuid import uuid4
from typing import List, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = FastAPI()

ruta_inicial = "/api/v2.2/"
base_url = "192.168.49.2:30080"

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
PASSWORD_GMAIL = os.getenv("PASSWORD_GMAIL")
MI_CORREO = os.getenv("MY_EMAIL")

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
def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None, time: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=time)
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

@app.post(ruta_inicial + "token_email", response_model=models.MostrarToken)
def login_for_access_token_with_username(form_data: models.UsuarioLoginWithEmail, db: Session = Depends(get_db)):
    user = db.query(UsuarioDB).filter(UsuarioDB.email == form_data.email).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.username, "role": user.rol.nombre}
    )
    return {
        "usuario_id": user.id,
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.rol.nombre
    }

@app.post(ruta_inicial + "token_username", response_model=models.MostrarToken)
def login_for_access_token_with_username(form_data: models.UsuarioLoginWithUsername, db: Session = Depends(get_db)):
    user = db.query(UsuarioDB).filter(UsuarioDB.username == form_data.username).first()
    print(user)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.username, "role": user.rol.nombre}
    )
    return {
        "usuario_id": user.id,
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.rol.nombre
    }


'''--------------------- USUARIOS ---------------------'''

@app.get(ruta_inicial + "usuarios", response_model=List[models.MostrarUsuario])
def obtener_usuarios(db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    return db.query(UsuarioDB).all()

@app.post(ruta_inicial + "usuarios", response_model=models.MostrarUsuario)
def crear_usuario(usuario: models.UsuarioCreacion, db: Session = Depends(get_db)):
    """ Crea un nuevo usuario con la contraseña hasheada """
    hashed_password = hash_password(usuario.password)  # Hasheamos la contraseña
    nuevo_usuario = UsuarioDB(username=usuario.username, password=hashed_password, email=usuario.email, rol_id=usuario.rol_id)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@app.get(ruta_inicial + "usuarios/{usuario_id}", response_model=models.MostrarUsuario)
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

def enviar_correo(destinatario: str, asunto: str, cuerpo: str):
    mensaje = MIMEMultipart()
    mensaje['From'] = MI_CORREO
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto
    mensaje.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(MI_CORREO, PASSWORD_GMAIL)
        servidor.sendmail(MI_CORREO, destinatario, mensaje.as_string())
        servidor.quit()
        print("Correo enviado correctamente")
    except Exception as e:
        print("Error al enviar correo:", e)

# Endpoint para solicitar cambio de contraseña
@app.post(ruta_inicial + "usuarios/cambiar_contrasena/{usuario_id}")
def pedir_cambio_contrasena(usuario_id: int, db: Session = Depends(get_db)):
    token = create_access_token(data={"sub": "cambiar_contrasena"}, time=15)
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    destinatario = usuario.email
    asunto = "Cambio de contrasena"
    mensaje = f"Para cambiar tu contrasena, haz clic en el siguiente enlace: http://{base_url}{ruta_inicial}usuarios/cambiar_contrasena/{usuario_id}/{token}"
    enviar_correo(destinatario=destinatario, asunto=asunto, cuerpo=mensaje)

    return {
        "mensaje": "Se ha enviado un correo para cambiar la contraseña",
    }

# Endpoint para realizar el cambio de contraseña
@app.post(ruta_inicial + "usuarios/cambiar_contrasena/{usuario_id}/{token}")
def cambiar_contrasena( usuario_id: int, token: str , datos: models.UsuarioCambioContrasena ,db: Session = Depends(get_db)):
    payload = verify_token(token)
    if payload is None or payload.get("sub") != "cambiar_contrasena":
        raise HTTPException(status_code=401, detail="Invalid token")

    # Verificar si el usuario existe
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Cambiar la contraseña
    hashed_password = hash_password(datos.nueva_contrasena)
    usuario.password = hashed_password
    db.commit()
    db.refresh(usuario)
    return {"message": "Contraseña cambiada exitosamente"}



'''--------------------- DISPOSITIVOS ---------------------'''

@app.get(ruta_inicial + "dispositivos", response_model=List[models.MostrarDispositivo])
def obtener_dispositivos(db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    return db.query(DispositivoDB).all()


def validacion_mac(mac):
    # Patrón para MAC con ':' o '-' como separador
    patron = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return re.match(patron, mac) is not None

@app.post(ruta_inicial + "dispositivos/{id_usuario}", response_model=models.MostrarDispositivo)
def crear_dispositivo(id_usuario: int,dispositivo: models.CrearDispositivo, db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    usuario_existente = db.query(UsuarioDB).filter(UsuarioDB.id == id_usuario).first()

    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not dispositivo.mac or not validacion_mac(dispositivo.mac):
        raise HTTPException(status_code=400, detail="MAC inválida. Debe tener el formato XX:XX:XX:XX:XX:XX o XX-XX-XX-XX-XX-XX")

    nuevo_dispositivo = DispositivoDB(active=dispositivo.active, nombre=dispositivo.nombre, usuario_id=id_usuario, mac=dispositivo.mac)
    db.add(nuevo_dispositivo)
    db.commit()
    db.refresh(nuevo_dispositivo)
    return nuevo_dispositivo

# Obtener dispositivo por id
@app.get(ruta_inicial + "dispositivos/{dispositivo_id}", response_model=models.MostrarDispositivo)
def obtener_dispositivo(dispositivo_id: int, db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    dispositivo = db.query(DispositivoDB).filter(DispositivoDB.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dispositivo

@app.get(ruta_inicial + "dispositivos/usuario/{usuario_id}", response_model=List[models.MostrarDispositivoSinUsuario])
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

@app.patch(ruta_inicial + "dispositivos/{dispositivo_id}", response_model=models.MostrarDispositivo)
def actualizar_dispositivo(dispositivo_id: int, dispositivo: models.ActualizarDispositivo, db: Session = Depends(get_db),current_user: UsuarioDB = Depends(get_current_user)):
    dispositivo_existente = db.query(DispositivoDB).filter(DispositivoDB.id == dispositivo_id).first()
    if not dispositivo_existente:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    if(dispositivo.mac is not None):
        if validacion_mac(dispositivo.mac):
            dispositivo_existente.mac = dispositivo.mac

    if(dispositivo.nombre is not None):
        dispositivo_existente.nombre = dispositivo.nombre
    
    if(dispositivo.active is not None):    
        dispositivo_existente.active = dispositivo.active

    db.commit()
    db.refresh(dispositivo_existente)
    return dispositivo_existente


'''--------------------- ROLES ---------------------'''
@app.get(ruta_inicial + "roles", response_model=List[models.Rol])
def obtener_roles(db: Session = Depends(get_db), current_user: UsuarioDB = Depends(get_current_user)):
    return db.query(RolDB).all()

'''--------------------- REGISTROS ---------------------'''

@app.get(ruta_inicial + "registros", response_model=List[models.MostrarRegistro])
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


@app.post(ruta_inicial + "registros", response_model=models.MostrarRegistro)
def crear_registro(registro: models.CrearRegistro, db: Session = Depends(get_db)):
    dispositivo_existente = db.query(DispositivoDB).filter(DispositivoDB.mac == registro.mac).first()
    if not dispositivo_existente:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    print(f"Dispositivo encontrado: {dispositivo_existente}")  
    if not registro.coordenadas:
        raise HTTPException(status_code=400, detail="Datos GNSS no proporcionados")

    # Llamamos a la función formateo para obtener las coordenadas
    coordenadas = formateo(registro.coordenadas)

    if coordenadas is None:
        raise HTTPException(status_code=400, detail="Datos GNSS inválidos o no disponibles")

    nuevo_registro = RegistroDB(
        coordenadas=coordenadas,  # Solo almacenamos las coordenadas
        dispositivo_id=dispositivo_existente.id
    )

    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return nuevo_registro

