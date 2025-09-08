from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Veritabanı URL'i
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vitamin_diagnosis.db")

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

def get_db():
    """Veritabanı session'ı döndürür"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
