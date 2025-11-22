from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '16d2f165d8d36cf388f7f481dbc7103ccfbb7f148048e0384d90f4a5cc24b89c'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl= '/auth/token')


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str

class UpdateUserRequest(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory='TodoApp/templates')


### Pages ###

@router.get('/login-page')
def render_login_page(request: Request):
    return templates.TemplateResponse('login.html', {'request':request})


@router.get('/register-page')
def render_register_page(request: Request):
    return templates.TemplateResponse('register.html', {'request':request})

### Endpoints
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int,role : str, expires_delta: timedelta,):

    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')

        if username is None or user_id is None:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                                detail= 'Could not validate user.')
        return  {'username': username, 'id': user_id, 'user_role': user_role}
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')


def require_user(user = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return user



@router.post('/auth/register', status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):

    existing_user = db.query(Users).filter(
        (Users.username == create_user_request.username) |
        (Users.email == create_user_request.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already exists."
        )

    new_user = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        phone_number=create_user_request.phone_number,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}

@router.put('/user/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
    user_id: int,
    updated_data: UpdateUserRequest,
    db: db_dependency,
    current_user: dict = Depends(get_current_user)
):
    if current_user['id'] != user_id and current_user['user_role'] != 'admin':
        raise HTTPException(status_code=401, detail="Not authorized")

    user_model = db.query(Users).filter(Users.id == user_id).first()

    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    # update only provided fields
    update_fields = updated_data.dict(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(user_model, key, value)

    db.commit()
    return {"message": "User updated"}
