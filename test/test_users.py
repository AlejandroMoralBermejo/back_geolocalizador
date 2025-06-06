import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db, UsuarioDB, RolDB, DispositivoDB, RegistroDB, get_password_hash

# Configuración de la base de datos de test
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5433/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------- FIXTURES ----------

@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        create_test_data(db)
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def token_de_admin(client):
    response = client.post("/api/v2.3/token_username", json={
        "username": "root",
        "password": "root"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def crear_usuario_temporal(db):
    user = UsuarioDB(
        username="temporal_user",
        password=get_password_hash("temporal"),
        email="temporal@example.com",
        rol_id=3  # user
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(user.id)
    return user.id


# ---------- CARGA DE DATOS DE PRUEBA ----------

def create_test_data(db):
    # Crear roles
    roles = [
        RolDB(nombre="root"),
        RolDB(nombre="admin"),
        RolDB(nombre="user"),
        RolDB(nombre="premium")
    ]
    db.add_all(roles)
    db.commit()
    for rol in roles:
        db.refresh(rol)

    # Crear usuarios
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
        RegistroDB(fecha=datetime.utcnow(), coordenadas="40.4168,-3.7038", mac=dispositivos[0].mac),
        RegistroDB(fecha=datetime.utcnow(), coordenadas="41.3851,2.1734", mac=dispositivos[1].mac),
    ]
    db.add_all(registros)
    db.commit()


# ---------- TESTS ----------

def test_get_users_authenticated(client, token_de_admin):
    response = client.get("/api/v2.3/usuarios", headers={"Authorization": f"Bearer {token_de_admin}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_user(client, token_de_admin, crear_usuario_temporal):
    user_id = crear_usuario_temporal
    print(user_id)
    response = client.delete(f"/api/v2.3/usuarios/{user_id}", headers={"Authorization": f"Bearer {token_de_admin}"})
    assert response.status_code == 404

