from pydantic import BaseModel, EmailStr



class UserBase(BaseModel):
    name: str
    email: EmailStr
    generation_count: int = 0    # it has a default value of 0. 
    prompts: list[str] = []

class UserIn(UserBase):
    password: str

class UserOut(UserBase):
    pass

class UserInDB(UserBase):
    hashed_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str



  