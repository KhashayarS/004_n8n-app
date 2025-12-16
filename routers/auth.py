from typing import Annotated
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from database import SessionLocal
from models import User


router = APIRouter(
    prefix="/auth",
    tags=[
        "auth",
    ],
)


SECRET_KEY = "614af5cb4b48a57e653bcdf3f8983bc3f9ce2bdecfe797d766715cc69b1830b5"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# oath2 = Annotated[OAuth2PasswordRequestForm, Depends()]
oath2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expired_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(tz=timezone.utc) + timedelta(minutes=expired_delta)
    encode.update({'exp': expires})
    return jwt.encode(encode, key=SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oath2_bearer)]):
    try:
        payload = jwt.decode(token, key=SECRET_KEY)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.") from exc
    

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    username = create_user_request.username
    password = create_user_request.password
    role = create_user_request.role

    hashed_password = bcrypt_context.hash(password)
    create_user_model = User(
        username=username,
        hashed_password=hashed_password,
        role=role,
        is_active=True
    )

    db.add(create_user_model)
    db.commit()
    

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    username = form_data.username
    password = form_data.password

    user = authenticate_user(username, password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=30))

    return {"access_token": token, "token_type": "Bearer"}
