import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db, UsuarioDB, DispositivoDB, get_password_hash

# URL de la base de datos de test
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5433/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_data(db):
    from database import RolDB, RegistroDB
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

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

    dispositivos = [
        DispositivoDB(mac="00:11:22:33:44:55", nombre="Sensor1", active=True, usuario_id=usuarios[0].id),
        DispositivoDB(mac="66:77:88:99:AA:BB", nombre="Sensor2", active=False, usuario_id=usuarios[1].id)
    ]
    db.add_all(dispositivos)
    db.commit()
    for dispositivo in dispositivos:
        db.refresh(dispositivo)

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
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def token(client):
    login_data = {"username": "root", "password": "root"}
    response = client.post("/api/v2.3/token_username", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token



### TESTS PARA DISPOSITIVOS ###



def test_get_all_dispositivos(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v2.3/dispositivos", headers=headers)
    assert response.status_code == 200

def test_crear_dispositivo(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response_users = client.get("/api/v2.3/usuarios", headers=headers)
    assert response_users.status_code == 200
    user_id = response_users.json()[0]["id"]

    print(user_id)

    nuevo_disp = {
        "mac": "AA:BB:CC:DD:EE:FF",
        "nombre": "DispositivoTest",
        "active": True
    }

    response = client.post(f"/api/v2.3/dispositivos/{user_id}", json=nuevo_disp, headers=headers)
    assert response.status_code == 200

def test_crear_dispositivo_mac_invalida(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response_users = client.get("/api/v2.3/usuarios", headers=headers)
    user_id = response_users.json()[0]["id"]

    nuevo_disp = {
        "mac": "INVALID_MAC",
        "nombre": "DispositivoMal",
        "active": True
    }
    response = client.post(f"/api/v2.3/dispositivos/{user_id}", json=nuevo_disp, headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"].startswith("MAC inválida")

def test_obtener_dispositivo_por_id(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v2.3/dispositivos", headers=headers)
    dispositivo_id = response.json()[0]["id"]

    response = client.get(f"/api/v2.3/dispositivos/{dispositivo_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == dispositivo_id

def test_eliminar_dispositivo(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v2.3/dispositivos", headers=headers)
    dispositivo_id = response.json()[0]["id"]

    response = client.delete(f"/api/v2.3/dispositivos/{dispositivo_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Dispositivo eliminado"

    response = client.get(f"/api/v2.3/dispositivos/{dispositivo_id}", headers=headers)
    assert response.status_code == 404

def test_actualizar_dispositivo(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v2.3/dispositivos", headers=headers)
    dispositivo = response.json()[0]
    dispositivo_id = dispositivo["id"]

    update_data = {
        "mac": "11:22:33:44:55:66",
        "nombre": "NuevoNombre",
        "active": False
    }

    response = client.patch(f"/api/v2.3/dispositivos/{dispositivo_id}", json=update_data, headers=headers)
    assert response.status_code == 200

def test_obtener_dispositivo_por_usuario(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response_users = client.get("/api/v2.3/usuarios", headers=headers)
    user_id = response_users.json()[0]["id"]

    response = client.get(f"/api/v2.3/dispositivos/usuario/{user_id}", headers=headers)
    if response.status_code == 404:
        assert response.json()["detail"] == "No se encontraron dispositivos para este usuario"
    else:
        assert response.status_code == 200
        assert isinstance(response.json(), list)
