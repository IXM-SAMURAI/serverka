from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.auth.service import AuthService

# Настройка базы данных (SQLite для примера)
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Схема аутентификации
security = HTTPBearer()

def get_db():
    """Зависимость для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Зависимость для получения сервиса аутентификации"""
    return AuthService(db)

def get_current_user(
    token: str = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Зависимость для получения текущего пользователя"""
    try:
        return auth_service.get_current_user(token.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )