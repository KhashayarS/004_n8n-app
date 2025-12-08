from sqlalchemy import Column, String, Integer, CheckConstraint, func
from database import Base


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    summary_by_ai = Column(String(300), nullable=True)
    category_by_ai = Column(String(300), nullable=True)

    __table_args__ = (
        CheckConstraint(func.length(author) >= 2, name='ck_author_min_length'),
    )
