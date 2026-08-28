from sqlalchemy import select

from app.core.security import verify_password
from app.models.user import User

def test_register_user_success(clinet):
    response = clinet.post(
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

def test_register_duplicate_email(clinet):
    payload = {
        "email": "charlie@example.com",
        "password": "12345678",
    }

    first_response = clinet.post(
        "/auth/register",
        json=payload,
    )

    second_response = clinet.post(
        "/auth/register",
        json=payload,
    )
    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json()["detail"] == "Email already registered"

def test_register_invalid_email(clinet):
    response = clinet.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": "12345678",
        },
    )

    assert response.status_code == 422

def test_register_short_password(clinet):
    response = clinet.post(
        "/auth/register",
        json={
            "email": "bob@example.com",
            "password": "123",
        },
    )

    assert response.status_code == 422

def test_registered_password_is_hashed(clinet, db_session):
    plain_password = "12345678"

    response = clinet.post(
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