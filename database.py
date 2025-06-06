import os
from sqlalchemy import create_engine, Column, String, Boolean, ForeignKey, DateTime, Integer, select
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
import datetime
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

usuarioDb = os.getenv("BBDD_USER")
passwordDb = os.getenv("BBDD_PASSWORD")
DATABASE_URL = f"postgresql://{usuarioDb}:{passwordDb}@127.0.0.1:5432/postgres"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

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
    mac = Column(String, unique=True, index=True, nullable=False)
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

def create_initial_roles_and_root():
    print("Analizando si existen roles...")
    with SessionLocal() as db:
        roles_exist = db.execute(select(RolDB).limit(1)).first()
        if not roles_exist:
            print("No existen roles. Creando roles y usuario root...")
            root_role = RolDB(nombre="root")
            admin_role = RolDB(nombre="admin")
            user_role = RolDB(nombre="user")
            premium_role = RolDB(nombre="premium")
            db.add_all([root_role, admin_role, user_role, premium_role])
            db.commit()

            root_user = UsuarioDB(
                username="root",
                password=get_password_hash("root"),
                email="root@root.root",
                rol_id=root_role.id
            )
            db.add(root_user)
            db.commit()
            print("Roles y usuario root creados.")
        else:
            print("Roles ya existen. No se hizo nada.")

Base.metadata.create_all(bind=engine)
create_initial_roles_and_root()  


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()