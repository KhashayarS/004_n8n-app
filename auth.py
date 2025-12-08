import requests
import json
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session

import models
from models import Book
from database import engine, SessionLocal