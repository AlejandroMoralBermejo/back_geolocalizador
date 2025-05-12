import os
from sqlalchemy import create_engine, Column, String, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime

# Ruta de la base de datos
DATABASE_PATH = "./gps_data.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definición de modelos
class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True, nullable=True)
    rol_id = Column(Integer, ForeignKey("roles.id"))

    dispositivos = relationship("DispositivoDB", back_populates="usuario", cascade="all, delete")
    rol = relationship("RolDB", back_populates="usuarios")

class DispositivoDB(Base):
    __tablename__ = "dispositivos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    active = Column(Boolean, default=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"))

    usuario = relationship("UsuarioDB", back_populates="dispositivos")
    registros = relationship("RegistroDB", back_populates="dispositivo", cascade="all, delete")

class RegistroDB(Base):
    __tablename__ = "registros"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
    coordenadas = Column(String)
    dispositivo_id = Column(Integer, ForeignKey("dispositivos.id", ondelete="CASCADE"))

    dispositivo = relationship("DispositivoDB", back_populates="registros")

class RolDB(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)   
    usuarios = relationship("UsuarioDB", back_populates="rol", cascade="all, delete")

# Verifica si la base de datos existe antes de crear las tablas
db_exists = os.path.exists(DATABASE_PATH)

# Crea las tablas
Base.metadata.create_all(bind=engine)

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Solo crear usuario root si la base de datos era nueva
if not db_exists:
    with SessionLocal() as db:
        # Crear roles primero
        root_role = RolDB(nombre="root")  # El usuario root es el super administrador
        admin_role = RolDB(nombre="admin")  # Los administradores
        user_role = RolDB(nombre="user")  # Los usuarios normales
        premium_role = RolDB(nombre="premium")  # Usuarios premium

        # Agregar roles a la base de datos
        db.add_all([root_role, admin_role, user_role, premium_role])
        db.commit()  # Commit para persistir los roles

        # Crear el usuario root con su rol asignado
        root_user = UsuarioDB(
            username="root",
            password=get_password_hash("root"),
            email="root@root.root",
            rol_id=root_role.id  # Asociar el rol al usuario
        )
        
        # Añadir el usuario root
        db.add(root_user)
        db.commit()  # Guardar el usuario root

