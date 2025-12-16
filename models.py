from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    CheckConstraint,
    func,
)
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String(100), nullable=True)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    summary_by_ai = Column(String(300), nullable=True)
    category_by_ai = Column(String(300), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    __table_args__ = (
        CheckConstraint(func.length(author) >= 2, name="ck_author_min_length"),
    )
