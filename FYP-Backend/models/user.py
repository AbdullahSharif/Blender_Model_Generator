from pydantic import BaseModel, EmailStr
from typing import List


class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    generation_count: int = 0    # it has a default value of 0. 
    prompts: List[str] = []


  