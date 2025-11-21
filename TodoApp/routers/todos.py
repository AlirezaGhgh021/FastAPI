from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from .auth import get_current_user
from ..models import Todos
from ..database import get_db
from ..routers.auth import require_user
from ..schemas import TodoResponse
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory='TodoApp/templates')

router = APIRouter(
    prefix = '/todos',
    tags = ['todos']
)

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

def redirect_to_login():
    redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key='access_token')
    return redirect_response

# Dependency type hints
DB = Session
User = dict

# Pages #
@router.get('/todo-page')
async def render_todo_page(request: Request,
                           db: DB = Depends(get_db)):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

        return templates.TemplateResponse('todo.html', {'request':request, "todos":todos, 'user':user})

    except:
        return redirect_to_login()


@router.get('/add-todo-page')
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse('add-todo.html', {'request': request, 'user': user})

    except:
        return redirect_to_login()



@router.get('/edit-todo-page/{todo_id}')
async def render_edit_todo_page(request: Request,
                                todo_id: int,
                                db: DB = Depends(get_db)):
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        return templates.TemplateResponse('edit-todo.html', {'request': request, 'todo': todo, 'user': user})

    except:
        return redirect_to_login()





#ENDPOINTS


# READ ALL TODOS
@router.get('/', response_model=List[TodoResponse], status_code=status.HTTP_200_OK)
async def read_all(
    user: User = Depends(require_user),
    db: DB = Depends(get_db)
):
    return db.query(Todos).filter(Todos.owner_id == user['id']).all()

# READ ONE TODO
@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(
    todo_id: int = Path(gt=0),
    user: User = Depends(require_user),
    db: DB = Depends(get_db)
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user['id']).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo_model

# CREATE TODO
@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_request: TodoRequest,
    user: User = Depends(require_user),
    db: DB = Depends(get_db)
):
    todo_model = Todos(**todo_request.model_dump(), owner_id=user['id'])
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

# UPDATE TODO
@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
    user: User = Depends(require_user),
    db: DB = Depends(get_db)
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user['id']).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail='Todo not found')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.commit()
    db.refresh(todo_model)
    return todo_model

# DELETE TODO
@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int = Path(gt=0),
    user: User = Depends(require_user),
    db: DB = Depends(get_db)
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user['id']).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.delete(todo_model)
    db.commit()
