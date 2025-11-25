from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from TodoApp.routers import auth, users, todos, admin
from TodoApp.database import engine
from TodoApp import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# STATIC FILES
app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")

# CORS (اختیاری)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Todo App is running"}
