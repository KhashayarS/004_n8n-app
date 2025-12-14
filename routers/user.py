from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from routers.auth import get_current_user
from database import SessionLocal
from models import User


router = APIRouter(
    prefix="/user",
    tags=[
        "user",
    ],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("")
def get_user(user_dict: user_dependency, db: db_dependency):
    user_id: int = user_dict.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
