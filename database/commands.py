from typing import Type

from .models import User
from sqlalchemy.orm import Session


def create_new_user(session: Session, username: str) -> None:
    user = User(username=username)
    session.add(user)
    session.commit()
    

def add_waste(session: Session, username: str, category: str, amount: float) -> None:
    user = session.get(User, username)
    user.__setattr__(category, user.__getattribute__(category) + amount)
    session.commit()


def get_user(session: Session, username: str) -> User | None:
    user = session.get(User, username)
    return user
