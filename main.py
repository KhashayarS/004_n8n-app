import requests
import json
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session

import models
from models import Book
from database import engine, SessionLocal


app = FastAPI(version='1.0.0')

models.Base.metadata.create_all(bind=engine)

# Helpers & Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Schemas
class BookRequest(BaseModel):
    title: str = Field(max_length=100)
    author: str = Field(max_length=100)

    model_config = {
        'json_schema_extra': {
            'example': {
                'title': 'My Favorite Book',
                'author': 'John Doe'
            }
        }
    }


@app.get('/book/{book_id}', status_code=status.HTTP_200_OK)
async def get_book(book_id: str, db: db_dependency):
    try:
        book = db.query(Book).filter(Book.id==book_id).first()
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to retrieve the book with id {book_id}: {e}')



@app.get('/books', status_code=status.HTTP_200_OK)
async def get_all_books(db: db_dependency):
    try:
        all_books = db.query(Book).all()
        return all_books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to retrieve books data: {e}')
    


@app.post('/add-book', status_code=status.HTTP_201_CREATED)
async def add_book(add_book_request: BookRequest, db: db_dependency):
    title = add_book_request.title
    author = add_book_request.author

    # Get info from N8N webhook
    WEBHOOK_URL = "https://khashayaar.app.n8n.cloud/webhook/a74903f3-186f-46de-a0ac-e3e142c0154b"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'title': title,
        'author': author
    }

    try:
        response = requests.post(WEBHOOK_URL, headers=headers, json=payload)
        response_content = json.loads(response.content)
        
        if 'output' in response_content:
            response_content = response_content.get('output')

        summary_by_ai = response_content['summary_by_ai']
        category_by_ai = response_content['category_by_ai']

    except Exception as e:
        raise HTTPException(status_code=502, detail=f'Error while connecting to N8N: {e}')
    
    new_book = Book(
        title=title,
        author=author,
        summary_by_ai=summary_by_ai,
        category_by_ai=category_by_ai
    )

    try:
        db.add(new_book)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Failed to store new data in database: {e}')
    

@app.get("/test-type/{test_value}")
async def print_test_value(test_value: int):
    return {'test_value': test_value}