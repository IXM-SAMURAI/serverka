from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_auth_service, get_current_user
from app.schemas.auth import (
    LoginRequest, 
    RegisterRequest, 
    UserResponse, 
    TokenResponse,
    MessageResponse
)
from app.auth.service import AuthService
from app.models.user import User

router = APIRouter()

@router.post(
    "/register", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя"
)
async def register(
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Регистрация нового пользователя в системе.
    
    - **username**: Имя пользователя (только латинские буквы, первая заглавная, мин. 7 символов)
    - **email**: Email пользователя (должен быть уникальным)
    - **password**: Пароль (мин. 8 символов, цифры, буквы в разных регистрах)
    - **c_password**: Подтверждение пароля
    - **birthday**: Дата рождения (формат: 2000-12-31, возраст от 14 лет)
    """
    try:
        user = auth_service.register_user(register_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Авторизация пользователя"
)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Авторизация пользователя в системе.
    
    - **username**: Имя пользователя
    - **password**: Пароль пользователя
    
    Возвращает пару токенов (access + refresh).
    """
    try:
        user = auth_service.authenticate_user(login_data)
        tokens = auth_service.create_tokens(user)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Информация о текущем пользователе"
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Получение информации об авторизованном пользователе.
    
    Требуется передача access token в заголовке Authorization.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        birthday=current_user.birthday
    )

@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Выход из системы"
)
async def logout(
    token: str = Depends(get_current_user),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Выход из системы (отзыв текущего токена).
    
    Отзывает используемый access token.
    """
    auth_service.logout(token, current_user)
    return MessageResponse(message="Успешный выход из системы")

@router.get(
    "/tokens",
    summary="Список активных токенов пользователя"
)
async def get_tokens(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Получение списка активных токенов авторизованного пользователя.
    
    Возвращает массив с информацией о токенах.
    """
    tokens = auth_service.get_user_tokens(current_user)
    return tokens

@router.post(
    "/logout_all",
    response_model=MessageResponse,
    summary="Выход из всех устройств"
)
async def logout_all(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Выход из всех устройств (отзыв всех токенов).
    
    Отзывает все активные токены пользователя.
    """
    auth_service.logout_all(current_user)
    return MessageResponse(message="Все токены успешно отозваны")

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Обновление токенов"
)
async def refresh_tokens(
    refresh_token: str = Body(..., embed=True),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Обновление пары токенов с помощью refresh token.
    
    - **refresh_token**: Refresh token для получения новой пары токенов
    
    При использовании уже использованного refresh token отзывает все токены пользователя.
    """
    try:
        tokens = auth_service.refresh_tokens(refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post(
    "/change_password",
    response_model=MessageResponse,
    summary="Смена пароля"
)
async def change_password(
    current_password: str = Body(..., embed=True, alias="currentPassword"),
    new_password: str = Body(..., embed=True, alias="newPassword"),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Смена пароля пользователя.
    
    - **currentPassword**: Текущий пароль (для подтверждения)
    - **newPassword**: Новый пароль
    
    После смены пароля все активные токены отзываются.
    """
    try:
        auth_service.change_password(current_user, current_password, new_password)
        return MessageResponse(message="Пароль успешно изменен")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )