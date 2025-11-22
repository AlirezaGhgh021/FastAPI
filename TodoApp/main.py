# this is the initial file I created

# from fastapi import FastAPI, Request, status
# from fastapi.staticfiles import StaticFiles
#
# from .models import Base
# from .database import engine
# from .routers import auth, todos, admin, users
# from fastapi.responses import RedirectResponse
#
#
# app = FastAPI()
#
# Base.metadata.create_all(bind=engine)
#
#
#
# app.mount('/static', StaticFiles(directory='TodoApp/static'), name='static')
#
# @app.get('/')
# def test(request: Request):
#     return RedirectResponse(url='/todos/todo-page', status_code=status.HTTP_302_FOUND)
#
#
#
#
# @app.get('/healthy')
# def health_check():
#     return {'status': 'Healthy'}
#
#
# app.include_router(auth.router)
# app.include_router(todos.router)
# app.include_router(admin.router)
# app.include_router(users.router)

# ----------------------------------

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .routers import auth, users, todos, admin

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def create_application() -> FastAPI:
    app = FastAPI(
        title="TodoApp",
        version="1.0.0",
        description="A fully featured backend Todo application built with FastAPI."
    )

    # Static
    static_path = ROOT_DIR / "static"
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    # Routers
    app.include_router(auth.router, prefix="/auth", tags=["Auth"])
    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(todos.router, prefix="/todos", tags=["Todos"])
    app.include_router(admin.router, prefix="/admin", tags=["Admin"])

    @app.get("/healthy")
    def health_check():
        return {"status": "healthy"}

    return app


app = create_application()
