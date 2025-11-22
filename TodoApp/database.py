# here is my file
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
#
# # SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:test123@localhost/TodoApplicationDatabase'
# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
# engine = create_engine(SQLALCHEMY_DATABASE_URL,
#                        connect_args={'check_same_thread':False}
#                        )
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
#
# Base = declarative_base()
#
#
# def get_db() -> Session:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

#------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from .core.config import settings

# Build DB URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
