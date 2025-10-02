from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import jwt  # Используем PyJWT вместо python-jose
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User, Token
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse, TokenResponse
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token
)
from app.core.config import settings

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, register_data: RegisterRequest) -> UserResponse:
        """Регистрация нового пользователя"""
        
        # Проверяем уникальность username (без учета регистра)
        existing_user = self.db.query(User).filter(
            User.username.ilike(register_data.username)
        ).first()
        if existing_user:
            raise ValueError("Пользователь с таким именем уже существует")

        # Проверяем уникальность email
        existing_email = self.db.query(User).filter(
            User.email == register_data.email
        ).first()
        if existing_email:
            raise ValueError("Пользователь с таким email уже существует")

        # Создаем нового пользователя
        user = User(
            username=register_data.username,
            email=register_data.email,
            password_hash=get_password_hash(register_data.password),
            birthday=register_data.birthday
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            birthday=user.birthday
        )

    def authenticate_user(self, login_data: LoginRequest) -> User:
        """Аутентификация пользователя"""
        
        # Ищем пользователя (без учета регистра)
        user = self.db.query(User).filter(
            User.username.ilike(login_data.username)
        ).first()
        
        if not user:
            raise ValueError("Неверное имя пользователя или пароль")
        
        if not verify_password(login_data.password, user.password_hash):
            raise ValueError("Неверное имя пользователя или пароль")
        
        if not user.is_active:
            raise ValueError("Учетная запись заблокирована")
        
        return user

    def create_tokens(self, user: User) -> TokenResponse:
        """Создание пары токенов (access + refresh)"""
        
        # Проверяем количество активных токенов
        active_tokens_count = self.db.query(Token).filter(
            and_(
                Token.user_id == user.id,
                Token.is_active == True,
                Token.expires_at > datetime.utcnow()
            )
        ).count()
        
        if active_tokens_count >= settings.MAX_ACTIVE_TOKENS:
            raise ValueError(f"Превышено максимальное количество активных токенов: {settings.MAX_ACTIVE_TOKENS}")

        # Создаем токены
        token_data = {"sub": str(user.id), "username": user.username}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Сохраняем хеши токенов в БД
        access_token_hash = get_password_hash(access_token)
        refresh_token_hash = get_password_hash(refresh_token)
        
        access_token_expires = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Сохраняем access token
        access_token_record = Token(
            user_id=user.id,
            token_hash=access_token_hash,
            expires_at=access_token_expires,
            token_type="access"
        )
        self.db.add(access_token_record)
        
        # Сохраняем refresh token
        refresh_token_record = Token(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=refresh_token_expires,
            token_type="refresh"
        )
        self.db.add(refresh_token_record)
        
        self.db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def get_current_user(self, token: str) -> User:
        """Получение текущего пользователя по токену"""
        
        payload = verify_token(token)
        if not payload:
            raise ValueError("Невалидный токен")
        
        if payload.get("type") != "access":
            raise ValueError("Требуется access token")
        
        user_id = int(payload.get("sub"))
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("Пользователь не найден")
        
        if not user.is_active:
            raise ValueError("Учетная запись заблокирована")
        
        # Проверяем, что токен активен в БД
        token_hash = get_password_hash(token)
        token_record = self.db.query(Token).filter(
            and_(
                Token.user_id == user.id,
                Token.token_hash == token_hash,
                Token.is_active == True,
                Token.expires_at > datetime.utcnow(),
                Token.token_type == "access"
            )
        ).first()
        
        if not token_record:
            raise ValueError("Токен отозван или истек")
        
        return user

    def logout(self, token: str, user: User) -> None:
        """Выход из системы (отзыв токена)"""
        
        token_hash = get_password_hash(token)
        token_record = self.db.query(Token).filter(
            and_(
                Token.user_id == user.id,
                Token.token_hash == token_hash,
                Token.is_active == True
            )
        ).first()
        
        if token_record:
            token_record.is_active = False
            self.db.commit()

    def logout_all(self, user: User) -> None:
        """Выход из всех устройств (отзыв всех токенов)"""
        
        self.db.query(Token).filter(
            and_(
                Token.user_id == user.id,
                Token.is_active == True
            )
        ).update({"is_active": False})
        self.db.commit()

    def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Обновление пары токенов"""
        
        payload = verify_token(refresh_token)
        if not payload:
            raise ValueError("Невалидный refresh token")
        
        if payload.get("type") != "refresh":
            raise ValueError("Требуется refresh token")
        
        user_id = int(payload.get("sub"))
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise ValueError("Пользователь не найден или заблокирован")
        
        # Проверяем валидность refresh token в БД
        refresh_token_hash = get_password_hash(refresh_token)
        refresh_token_record = self.db.query(Token).filter(
            and_(
                Token.user_id == user.id,
                Token.token_hash == refresh_token_hash,
                Token.is_active == True,
                Token.expires_at > datetime.utcnow(),
                Token.token_type == "refresh"
            )
        ).first()
        
        if not refresh_token_record:
            # Если refresh token невалиден, отзываем все токены пользователя
            self.logout_all(user)
            raise ValueError("Refresh token невалиден или уже использован")
        
        # Отзываем использованный refresh token
        refresh_token_record.is_active = False
        self.db.commit()
        
        # Создаем новую пару токенов
        return self.create_tokens(user)

    def get_user_tokens(self, user: User) -> List[Dict[str, Any]]:
        """Получение списка активных токенов пользователя"""
        
        tokens = self.db.query(Token).filter(
            and_(
                Token.user_id == user.id,
                Token.is_active == True,
                Token.expires_at > datetime.utcnow()
            )
        ).all()
        
        return [
            {
                "id": token.id,
                "token_type": token.token_type,
                "created_at": token.created_at,
                "expires_at": token.expires_at,
                "is_active": token.is_active
            }
            for token in tokens
        ]

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        """Смена пароля пользователя"""
        
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Текущий пароль неверен")
        
        # Валидация нового пароля
        if len(new_password) < 8:
            raise ValueError("Минимальная длина 8 символов")
        if not any(char.isdigit() for char in new_password):
            raise ValueError("Должен содержать хотя бы одну цифру")
        if not any(char.isalpha() for char in new_password):
            raise ValueError("Должен содержать хотя бы одну букву")
        if not any(char.isupper() for char in new_password):
            raise ValueError("Должен содержать хотя бы одну заглавную букву")
        if not any(char.islower() for char in new_password):
            raise ValueError("Должен содержать хотя бы одну строчную букву")
        
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        
        # Отзываем все токены пользователя при смене пароля
        self.logout_all(user)