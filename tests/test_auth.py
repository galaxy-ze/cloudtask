from sqlalchemy import select

from app.core.security import create_access_token, verify_password
from app.models.user import User

def test_register_user_success(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "password": "12345678",
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "alice@example.com"
    assert isinstance(data["id"], int)

    assert "password" not in data
    assert "password_hash" not in data

def test_register_duplicate_email(client):
    payload = {
        "email": "charlie@example.com",
        "password": "12345678",
    }

    first_response = client.post(
        "/auth/register",
        json=payload,
    )

    second_response = client.post(
        "/auth/register",
        json=payload,
    )
    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json()["detail"] == "Email already registered"

def test_register_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": "12345678",
        },
    )

    assert response.status_code == 422

def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "bob@example.com",
            "password": "123",
        },
    )

    assert response.status_code == 422

def test_registered_password_is_hashed(client, db_session):
    plain_password = "12345678"

    response = client.post(
        "/auth/register",
        json={
            "email": "charlie@example.com",
            "password": plain_password,
        },
    )

    assert response.status_code == 201

    user = db_session.scalar(
        select(User).where(
            User.email == "charlie@example.com"
        )
    )

    assert user is not None

    assert user.password_hash != plain_password

    assert verify_password(
        plain_password,
        user.password_hash,
    )

def register_test_user(client):
    return client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "password": "12345678"
        }
    )

def test_login_success(client):
    register_test_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "alice@example.com",
            "password": "12345678"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert isinstance(data["access_token"],str)
    assert len(data["access_token"]) > 0

    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    register_test_user(client)
    response = client.post(
        "/auth/login",
        json={
            "email": "alice@example.com",
            "password": "12345678213123"
        }
    )
    assert response.status_code == 401
    assert (
        response.json()["detail"] == "Invalid email or password"
    )

def test_login_user_not_found(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "12345678"
        }
    )
    assert response.status_code == 401

    assert (
        response.json()["detail"]
        == "Invalid email or password"
    )


def test_get_current_user_with_valid_token(client):
    register_test_user(client)

    login_response = client.post(
        "/auth/login",
        json = {
            "email": "alice@example.com",
            "password": "12345678"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "alice@example.com"
    assert isinstance(data["id"], int)
    assert "password" not in data
    assert "password_hash" not in data

def test_get_current_user_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code in (401,403)

def test_get_current_user_with_invalid_token(client):
    response = client.get(
        "auth/me",
        headers={
            "Authorization": "Bearer not-a-valid-jwt"
        }
    )
    assert response.status_code == 401

    assert (
        response.json()["detail"] == "Invalid authentication credentials"
    )

def test_get_current_user_not_found(client):
    access_token = create_access_token(999999)

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 401

    assert (
        response.json()["detail"]
        == "Invalid authentication credentials"
    )