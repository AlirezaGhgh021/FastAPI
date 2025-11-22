from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..models import Todos
from ..database import get_db
from ..schemas import TodoResponse
from ..routers.auth import require_user
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)

templates = Jinja2Templates(directory='TodoApp/templates')

# ---------------------
# Schemas
# ---------------------
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool = False

# ---------------------
# Helpers
# ---------------------
def redirect_to_login():
    redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key='access_token')
    return redirect_response

# ---------------------
# Pages
# ---------------------
@router.get('/todo-page')
def render_todo_page(request: Request, db: Session = Depends(get_db), user: dict = Depends(require_user)):
    todos = db.query(Todos).filter(Todos.owner_id == user['id']).all()
    return templates.TemplateResponse('todo.html', {'request': request, 'todos': todos, 'user': user})

@router.get('/add-todo-page')
def render_add_todo_page(request: Request, user: dict = Depends(require_user)):
    return templates.TemplateResponse('add-todo.html', {'request': request, 'user': user})

@router.get('/edit-todo-page/{todo_id}')
def render_edit_todo_page(request: Request, todo_id: int, db: Session = Depends(get_db), user: dict = Depends(require_user)):
    todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user['id']).first()
    if not todo:
        raise HTTPException(status_code=404, detail='Todo not found')
    return templates.TemplateResponse('edit-todo.html', {'request': request, 'todo': todo, 'user': user})

# ---------------------
# API Endpoints
# ---------------------
@router.get('/', response_model=List[TodoResponse])
def read_all_todos(user: dict = Depends(require_user), db: Session = Depends(get_db)):
    return db.query(Todos).filter(Todos.owner_id == user['id']).all()

@router.get('/todo/{todo_id}', response_model=TodoResponse)
def read_todo(todo_id: int = Path(gt=0), user: dict = Depends(require_user), db: Session = Depends(get_db)):
    todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user['id']).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.post('/todo', response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo_request: TodoRequest, user: dict = Depends(require_user), db: Session = Depends(get_db)):
    todo = Todos(**todo_request.model_dump(), owner_id=user['id'])
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@router.put('/todo/{todo_id}', status_code=status.HTTP_200_OK, response_model=TodoResponse)
def update_todo(todo_request: TodoRequest, todo_id: int = Path(gt=0), user: dict = Depends(require_user), db: Session = Depends(get_db)):
    todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user['id']).first()
    if not todo:
        raise HTTPException(status_code=404, detail='Todo not found')
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete
    db.commit()
    db.refresh(todo)
    return todo

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int = Path(gt=0), user: dict = Depends(require_user), db: Session = Depends(get_db)):
    todo = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user['id']).first()
    if not todo:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.delete(todo)
    db.commit()

