from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.schemas.role import UserRoleResponse, UserRoleCreate
from app.models.role import UserRole, Role
from app.models.user import User

router = APIRouter(prefix="/api/ref/policy/role", tags=["roles"])

@router.get("/")
def get_roles():
    return {"message": "Roles router works"}

@router.get("/{user_id}/role", response_model=List[UserRoleResponse])
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение ролей пользователя"""
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.is_active == True
    ).all()
    return user_roles

@router.post("/{user_id}/role", response_model=UserRoleResponse)
def assign_role_to_user(
    user_id: int,
    role_data: UserRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Присвоение ролей пользователю"""
    # Проверяем существование пользователя
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем существование роли
    role = db.query(Role).filter(Role.id == role_data.role_id, Role.is_active == True).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Проверяем, не назначена ли уже эта роль
    existing_user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_data.role_id,
        UserRole.is_active == True
    ).first()
    
    if existing_user_role:
        raise HTTPException(status_code=400, detail="Role already assigned to user")
    
    user_role = UserRole(
        user_id=user_id,
        role_id=role_data.role_id,
        created_by=current_user.id
    )
    db.add(user_role)
    db.commit()
    db.refresh(user_role)
    return user_role

@router.delete("/{user_id}/role/{role_id}")
def remove_role_from_user_hard(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Жесткое удаление роли у пользователя"""
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()
    
    if not user_role:
        raise HTTPException(status_code=404, detail="User role not found")
    
    db.delete(user_role)
    db.commit()
    return {"message": "User role deleted successfully"}

@router.delete("/{user_id}/role/{role_id}/soft")
def remove_role_from_user_soft(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Мягкое удаление роли у пользователя"""
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
        UserRole.is_active == True
    ).first()
    
    if not user_role:
        raise HTTPException(status_code=404, detail="User role not found")
    
    user_role.is_active = False
    user_role.deleted_by = current_user.id
    db.commit()
    return {"message": "User role soft deleted successfully"}

@router.post("/{user_id}/role/{role_id}/restore")
def restore_user_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Восстановление мягко удаленной роли у пользователя"""
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
        UserRole.is_active == False
    ).first()
    
    if not user_role:
        raise HTTPException(status_code=404, detail="User role not found or already active")
    
    user_role.is_active = True
    user_role.deleted_by = None
    db.commit()
    return {"message": "User role restored successfully"}