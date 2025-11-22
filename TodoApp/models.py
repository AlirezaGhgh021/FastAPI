# my file:
#
# from .database import Base
# from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
#
#
# class Users(Base):
#     __tablename__ = 'users'
#
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True)
#     username = Column(String, unique=True)
#     first_name = Column(String)
#     last_name = Column(String)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)
#     role = Column(String)
#     phone_number = Column(String)
#
#
#
#
# class Todos(Base):
#     __tablename__ = 'todos'
#
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String)
#     description = Column(String)
#     priority = Column(Integer)
#     complete = Column(Boolean, default=False)
#     owner_id = Column(Integer, ForeignKey('users.id'))

# -------------------------
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    func,
    Enum
)
from sqlalchemy.orm import relationship
from .database import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, index=True, nullable=False)
    username = Column(String(64), unique=True, index=True, nullable=False)
    first_name = Column(String(64))
    last_name = Column(String(64))
    phone_number = Column(String(32))
    hashed_password = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.user)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ORM relationship
    todos = relationship(
        "Todos",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    description = Column(String(512))
    priority = Column(Integer, index=True)
    complete = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey("users.id"), index=True)
    owner = relationship("Users", back_populates="todos")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Todo {self.title}>"
