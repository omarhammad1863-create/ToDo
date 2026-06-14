from typing import Annotated
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from ..models import Users
from ..database import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext


router = APIRouter(
    prefix="/users",
    tags=["users"]
)
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class PhoneNumberRequest(BaseModel):
    phone_number: str


class ChangePasswordRequest(BaseModel):
    password: str
    new_password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    phone_number: str | None
    is_active: bool


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, change_password_request: ChangePasswordRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not bcrypt_context.verify(change_password_request.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password change")
    user_model.hashed_password = bcrypt_context.hash(change_password_request.new_password)
    db.commit()


@router.put("/phonenumber", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number_request: PhoneNumberRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_model.phone_number = phone_number_request.phone_number
    db.commit()
