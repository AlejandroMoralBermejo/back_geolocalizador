def test_login_with_email(client):
    response = client.post("/api/v2.3/token_email", json={
        "email": "root@root.root",
        "password": "root"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "root"
    assert isinstance(data["usuario_id"], int)


def test_login_with_username(client):
    response = client.post("/api/v2.3/token_username", json={
        "username": "root",
        "password": "root"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "root"
    assert isinstance(data["usuario_id"], int)


def test_login_with_email_wrong_password(client):
    response = client.post("/api/v2.3/token_email", json={
        "email": "root@root.root",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_with_username_not_found(client):
    response = client.post("/api/v2.3/token_username", json={
        "username": "nonexistent_user",
        "password": "doesntmatter"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
