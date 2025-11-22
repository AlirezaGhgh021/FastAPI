from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from ..models import Todos
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# ---------------------
# Endpoints
# ---------------------
@router.get('/todos')
def read_all_todos(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized')
    return db.query(Todos).all()

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int = Path(gt=0), user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized')
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found')
    db.delete(todo)
    db.commit()
