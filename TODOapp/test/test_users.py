from fastapi import status

from .utils import *
from ..routers.users import get_db, get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "codingwithrobytest"
    assert response.json()["email"] == "codingwithrobytest@email.com"
    assert response.json()["first_name"] == "Eric"
    assert response.json()["last_name"] == "Roby"
    assert response.json()["role"] == "admin"
    assert response.json()["phone_number"] == "(111)-111-1111"
    assert "hashed_password" not in response.json()


def test_change_password_success(test_user):
    response = client.put(
        "/users/password",
        json={
            "password": "testpassword",
            "new_password": "newpassword"
        }
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert bcrypt_context.verify("newpassword", model.hashed_password)
