from .utils import *
from datetime import timedelta
import pytest
from fastapi import HTTPException
from jose import jwt
from ..routers.auth import authenticate_user, create_access_token, get_current_user, SECRET_KEY, ALGORITHM


def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, "testpassword", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user("WrongUserName", "testpassword", db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.username, "wrongpassword", db)
    assert wrong_password_user is False


def test_create_user_defaults_to_user_role():
    request_data = {
        "username": "publicuser",
        "email": "publicuser@example.com",
        "first_name": "Public",
        "last_name": "User",
        "password": "testpassword",
        "phone_number": "(222)-222-2222",
        "role": "admin",
    }

    response = client.post("/auth/", json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    try:
        model = db.query(Users).filter(Users.username == request_data["username"]).first()
        assert model is not None
        assert model.role == "user"
        assert bcrypt_context.verify(request_data["password"], model.hashed_password)
    finally:
        db.close()

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users WHERE username = 'publicuser';"))
        connection.commit()


def test_create_access_token():
    username = "testuser"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_signature": False}
    )

    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["role"] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {"sub": "testuser", "id": 1, "role": "admin"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)

    assert user == {"username": "testuser", "id": 1, "user_role": "admin"}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {"role": "user"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate user."
