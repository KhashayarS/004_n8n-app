from typing import Annotated
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from database import SessionLocal
from models import User


SECRET_KEY = "614af5cb4b48a57e653bcdf3f8983bc3f9ce2bdecfe797d766715cc69b1830b5"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="/auth",
    tags=[
        "auth",
    ],
)

oath2 = Annotated[OAuth2PasswordRequestForm, Depends()]
oath2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
db_dependency = Annotated[Session, Depends(get_db)]


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username, password, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oath2_bearer)]):
    try:
        payload = jwt.decode(token, key=SECRET_KEY)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")

        return {"username": username, "id": user_id, "role": role}
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Authentication failed: {e}") from e


def create_token(username: str, user_id: int, role: str):
    expiration_time = datetime.now(tz=timezone.utc) + timedelta(minutes=30)

    payload = {"sub": username, "id": user_id, "exp": expiration_time, "role": role}

    token = jwt.encode(payload, key=SECRET_KEY, algorithm=ALGORITHM)

    return token


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: oath2, db: db_dependency):
    username = form_data.username
    password = form_data.password

    user = authenticate_user(username, password, db)

    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed.")

    access_token = create_token(user.username, user.id, user.role)

    return {"access_token": access_token, "token_type": "Bearer"}


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(form_data: oath2, db: db_dependency):
    username = form_data.username
    password = form_data.password

    hashed_password = bcrypt_context.hash(password)
    new_user = User(username=username, hashed_password=hashed_password)

    try:
        db.add(new_user)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Signup failed.") from e
