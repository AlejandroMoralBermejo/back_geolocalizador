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

    dispositivos = relationship("DispositivoDB", back_populates="usuario", cascade="all, delete")

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
        root_user = UsuarioDB(
            username="root",
            password=get_password_hash("root"),  # Hasheamos aquí
            email="root@root.root"
        )
        db.add(root_user)
        db.commit()
