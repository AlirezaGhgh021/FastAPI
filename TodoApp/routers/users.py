from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from ..models import Users
from ..database import get_db
from ..routers.auth import get_current_user, bcrypt_context

router = APIRouter(
    prefix='/users',
    tags=['users']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# ---------------------
# Schemas
# ---------------------
class UserVerification(BaseModel):
    old_password: str
    new_password: str

class UpdateEmailRequest(BaseModel):
    email: EmailStr

class UpdatePhoneRequest(BaseModel):
    phone_number: str

# ---------------------
# Endpoints
# ---------------------
@router.get('/me')
def get_me(db: db_dependency, user: dict = Depends(get_current_user)):
    user_model = db.query(Users).filter(Users.id == user['id']).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user_model

@router.put('/change-password', status_code=status.HTTP_204_NO_CONTENT)
def change_password(data: UserVerification, db: db_dependency, user: dict = Depends(get_current_user)):
    user_model = db.query(Users).filter(Users.id == user['id']).first()
    if not bcrypt_context.verify(data.old_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Old password incorrect')
    user_model.hashed_password = bcrypt_context.hash(data.new_password)
    db.commit()

@router.put('/update-email', status_code=status.HTTP_204_NO_CONTENT)
def update_email(data: UpdateEmailRequest, db: db_dependency, user: dict = Depends(get_current_user)):
    user_model = db.query(Users).filter(Users.id == user['id']).first()
    user_model.email = data.email
    db.commit()

@router.put('/update-phone', status_code=status.HTTP_204_NO_CONTENT)
def update_phone(data: UpdatePhoneRequest, db: db_dependency, user: dict = Depends(get_current_user)):
    user_model = db.query(Users).filter(Users.id == user['id']).first()
    user_model.phone_number = data.phone_number
    db.commit()


