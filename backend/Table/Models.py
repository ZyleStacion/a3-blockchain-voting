from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str   # in real app -> hash this

class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr

class Vote(BaseModel):
    user_id: str
    charity_id: str
    tickets: int   # quadratic voting = tickets^2

class Transaction(BaseModel):
    user_id: str
    amount: float
