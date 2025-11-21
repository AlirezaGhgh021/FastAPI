from typing import Annotated
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, APIRouter
from starlette import status
from typing_extensions import deprecated
from ..models import Users
from ..database import  SessionLocal
from .auth import get_current_user, bcrypt_context
from passlib.context import CryptContext


router = APIRouter(
    prefix='/users',
    tags=['users']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.get('/me')
async def get_user(
        db: db_dependency,
        current_user: dict=Depends(get_current_user)
):
    user = db.query(Users).filter(Users.id == current_user.get('id')).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found')
    return user
    # return {
    #     'username': user.username,
    #     'email': user.email,
    #     'first_name': user.first_name,
    #     'last_name': user.last_name,
    #     'role': user.role,
    #     'is_active': user.is_active
    # }


class UserVerification(BaseModel):
    old_password: str
    new_password: str


@router.put('/change-password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
        db: db_dependency,
        user_verification: UserVerification,
        user: user_dependency
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.old_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='old password is incorrect')

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()



class UpdatePhoneNumberRequest(BaseModel):
    phone_number: str

@router.put('/update-phone/{phone_number}',status_code=status.HTTP_204_NO_CONTENT)
async def update_phone(db : db_dependency,
                       phone_number: str,
                       current_user : user_dependency):
    user = db.query(Users).filter(Users.id == current_user.get('id')).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    user.phone_number = phone_number
    db.add(user)
    db.commit()

class UpdateEmailRequest(BaseModel):
    email: EmailStr

@router.put('/update-email', status_code=status.HTTP_204_NO_CONTENT)
async def update_email(db: db_dependency,
                       request : UpdateEmailRequest,
                       current_user : dict =Depends(get_current_user)):
    user = db.query(Users).filter(Users.id == current_user.get('id')).first()
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    user.email = request.email
    db.add(user)
    db.commit()

