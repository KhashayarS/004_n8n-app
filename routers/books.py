import requests
import json
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import APIRouter, status, HTTPException, Depends, Path
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Book
from routers.auth import get_current_user


router = APIRouter(prefix="/books", tags=["books"])


# Helpers & Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# Schemas
class BookRequest(BaseModel):
    title: str = Field(max_length=100)
    author: str = Field(max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {"title": "Deep Work", "author": "Cal Newport"}
        }
    }


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_books(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    owner_id = user.get("id")
    try:
        all_books = db.query(Book).filter(Book.owner_id == owner_id).all()
        return all_books
    except Exception as e:
        raise HTTPException(status_code=500) from e


@router.get("/{book_id}", status_code=status.HTTP_200_OK)
async def get_book(
    db: db_dependency, user: user_dependency, book_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    owner_id = user.get("id")
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
        .filter(Book.owner_id == owner_id)
        .first()
    )
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    return book


@router.post("/add-book", status_code=status.HTTP_201_CREATED)
async def add_book(
    add_book_request: BookRequest, db: db_dependency, user: user_dependency
):
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    title = add_book_request.title
    author = add_book_request.author

    owner_id = user.get("id")
    if not owner_id:
        raise HTTPException(status_code=401, detail="Authentication Failed.")

    # Get info from N8N webhook
    WEBHOOK_URL = (
        "https://mixedow.app.n8n.cloud/webhook/5f35682b-c591-4f2d-a479-24cca7718232"
    )
    headers = {"Content-Type": "application/json"}
    payload = {"title": title, "author": author}

    try:
        response = requests.post(
            WEBHOOK_URL, headers=headers, json=payload, timeout=60000
        )
        response_content = json.loads(response.content)

        if "output" in response_content:
            response_content = response_content.get("output")

        summary_by_ai = response_content["summary_by_ai"]
        category_by_ai = response_content["category_by_ai"]

    except Exception as e:
        raise HTTPException(status_code=500) from e

    new_book = Book(
        title=title,
        author=author,
        summary_by_ai=summary_by_ai,
        category_by_ai=category_by_ai,
        owner_id=owner_id,
    )

    try:
        db.add(new_book)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500) from e


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    db: db_dependency, user: user_dependency, book_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    owner_id = user.get("id")
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
        .filter(Book.owner_id == owner_id)
        .first()
    )

    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    try:
        db.delete(book)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500) from e
