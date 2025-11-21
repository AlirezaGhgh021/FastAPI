
from pydantic import BaseModel

class TodoBase(BaseModel):
    title: str
    description: str
    priority: int
    complete: bool

class TodoResponse(TodoBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
