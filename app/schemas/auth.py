from pydantic import BaseModel, EmailStr, validator
from datetime import date, datetime
from typing import Optional, List
import re

class LoginRequest(BaseModel):
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 7:
            raise ValueError('Минимальная длина 7 символов')
        if not v[0].isupper():
            raise ValueError('Должен начинаться с большой буквы')
        if not re.match(r'^[A-Za-z]+$', v):
            raise ValueError('Только буквы латинского алфавита')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Минимальная длина 8 символов')
        if not any(char.isdigit() for char in v):
            raise ValueError('Должен содержать хотя бы одну цифру')
        if not any(char.isalpha() for char in v):
            raise ValueError('Должен содержать хотя бы одну букву')
        if not any(char.isupper() for char in v):
            raise ValueError('Должен содержать хотя бы одну заглавную букву')
        if not any(char.islower() for char in v):
            raise ValueError('Должен содержать хотя бы одну строчную букву')
        return v

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    c_password: str
    birthday: date
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 7:
            raise ValueError('Минимальная длина 7 символов')
        if not v[0].isupper():
            raise ValueError('Должен начинаться с большой буквы')
        if not re.match(r'^[A-Za-z]+$', v):
            raise ValueError('Только буквы латинского алфавита')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Минимальная длина 8 символов')
        if not any(char.isdigit() for char in v):
            raise ValueError('Должен содержать хотя бы одну цифру')
        if not any(char.isalpha() for char in v):
            raise ValueError('Должен содержать хотя бы одну букву')
        if not any(char.isupper() for char in v):
            raise ValueError('Должен содержать хотя бы одну заглавную букву')
        if not any(char.islower() for char in v):
            raise ValueError('Должен содержать хотя бы одну строчную букву')
        return v
    
    @validator('c_password')
    def validate_c_password(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v
    
    @validator('birthday')
    def validate_birthday(cls, v):
        age = (date.today() - v).days // 365
        if age < 14:
            raise ValueError('Возраст должен быть не менее 14 лет')
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    birthday: date
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenInfo(BaseModel):
    id: int
    created_at: datetime
    expires_at: datetime
    is_active: bool

class MessageResponse(BaseModel):
    message: str