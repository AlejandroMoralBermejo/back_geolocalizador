import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from database import Base, UsuarioDB, RolDB, DispositivoDB, RegistroDB, get_password_hash

# Cambia aquí la URL para test_db (ajusta usuario, password, host, puerto, nombre DB)
TEST_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5433/test_db"

engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_data(db):
    # Crear roles de prueba
    roles = [
        RolDB(nombre="root"),
        RolDB(nombre="admin"),
        RolDB(nombre="user"),
        RolDB(nombre="premium")
    ]
    db.add_all(roles)
    db.commit()

    # Refrescar para obtener ids generados
    for rol in roles:
        db.refresh(rol)

    # Crear usuarios con contraseñas hasheadas
    usuarios = [
        UsuarioDB(
            username="root",
            password=get_password_hash("root"),
            email="root@root.root",
            rol_id=roles[0].id
        ),
        UsuarioDB(
            username="admin_user",
            password=get_password_hash("admin123"),
            email="admin@example.com",
            rol_id=roles[1].id
        ),
        UsuarioDB(
            username="normal_user",
            password=get_password_hash("user123"),
            email="user@example.com",
            rol_id=roles[2].id
        )
    ]
    db.add_all(usuarios)
    db.commit()

    for usuario in usuarios:
        db.refresh(usuario)

    # Crear dispositivos
    dispositivos = [
        DispositivoDB(mac="00:11:22:33:44:55", nombre="Sensor1", active=True, usuario_id=usuarios[0].id),
        DispositivoDB(mac="66:77:88:99:AA:BB", nombre="Sensor2", active=False, usuario_id=usuarios[1].id)
    ]
    db.add_all(dispositivos)
    db.commit()

    for dispositivo in dispositivos:
        db.refresh(dispositivo)

    # Crear registros
    from datetime import datetime
    registros = [
        RegistroDB(fecha=datetime.utcnow(), coordenadas="40.4168,-3.7038", dispositivo_id=dispositivos[0].id),
        RegistroDB(fecha=datetime.utcnow(), coordenadas="41.3851,2.1734", dispositivo_id=dispositivos[1].id),
    ]
    db.add_all(registros)
    db.commit()

def main():
    print("Eliminando y creando tablas en test_db...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas.")

    db = SessionLocal()
    try:
        create_test_data(db)
        print("Datos de prueba insertados.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
