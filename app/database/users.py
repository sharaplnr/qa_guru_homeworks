from typing import Iterable

from fastapi import HTTPException
from sqlmodel import Session, select
from .engine import engine
from ..models.User import User


def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)

def get_users(session: Session) -> Iterable[User]:
    statement = select(User)
    return session.execute(statement).scalars().all()

def create_user(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def update_user(session: Session, user_id: int, user: User) -> User:
    db_user = get_user(session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def delete_user(session: Session, user_id: int):
    user = get_user(session, user_id)
    if user:
        session.delete(user)
        session.commit()
    return user


