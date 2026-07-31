"""Declarative base for all ORM models.

All models should inherit from Base:

    class User(Base):
        __tablename__ = "users"
        ...
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
