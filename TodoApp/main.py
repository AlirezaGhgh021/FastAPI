from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

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

    @app.get("/")
    def root():
        return RedirectResponse(url="/auth/login-page")


    @app.get("/healthy")
    def health_check():
        return {"status": "healthy"}

    return app


app = create_application()
