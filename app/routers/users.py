from http import HTTPStatus
from typing import Iterable

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from app.models.User import User, UserCreate, UserUpdate
from app.database.engine import get_session
from app.database import users

router = APIRouter(prefix="/api/users")

@router.get("/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int, session: Session = Depends(get_session)) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")

    user = users.get_user(session, user_id)

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user

@router.get("/", status_code=HTTPStatus.OK)
def get_users(session: Session = Depends(get_session)) -> Iterable[User]:
    return users.get_users(session)

@router.post("/", status_code=HTTPStatus.CREATED)
def create_user(user: User, session: Session = Depends(get_session)) -> User:
    UserCreate.model_validate(user.model_dump())
    return users.create_user(session, user)

@router.patch("/{user_id}", status_code=HTTPStatus.OK)
def update_user(user_id: int, user: User, session: Session = Depends(get_session)) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    UserUpdate.model_validate(user.model_dump())
    return users.update_user(session, user_id, user)

@router.delete("/{user_id}", status_code=HTTPStatus.OK)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    users.delete_user(session, user_id)
    return {"message": "User deleted"}


