from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TodoApp"
    VERSION: str = "1.0.0"

    DATABASE_URL: str = "sqlite:///./todosapp.db"

    class Config:
        env_file = ".env"


settings = Settings()
