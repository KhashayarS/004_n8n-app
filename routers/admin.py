from typing import Annotated
from fastapi import APIRouter, status, HTTPException, Depends, Path
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Book
from routers.auth import get_current_user


router = APIRouter(prefix="/admin", tags=["admin"])


# Helpers & Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_books(db: db_dependency, user: user_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    try:
        all_books = db.query(Book).all()
        return all_books
    except Exception as e:
        raise HTTPException(status_code=500) from e


@router.get("/{book_id}", status_code=status.HTTP_200_OK)
async def get_book( db: db_dependency, user: user_dependency, book_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found.")

    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(db: db_dependency, user: user_dependency, book_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found.")

    try:
        db.delete(book)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500) from e
