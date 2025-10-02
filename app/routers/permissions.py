from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.schemas.role import PermissionResponse, PermissionCreate, PermissionUpdate
from app.models.role import Permission
from app.models.user import User  # Добавляем импорт User

router = APIRouter(prefix="/api/ref/policy/permission", tags=["permissions"])

@router.get("/")
def get_permissions():
    return {"message": "Permissions router works"}

@router.get("/", response_model=List[PermissionResponse])
def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Теперь User импортирован
):
    """Получение списка разрешений"""
    permissions = db.query(Permission).filter(Permission.is_active == True).all()
    return permissions

@router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение конкретного разрешения"""
    permission = db.query(Permission).filter(Permission.id == permission_id, Permission.is_active == True).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

@router.post("/", response_model=PermissionResponse)
def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание разрешения"""
    # Проверка уникальности
    existing_permission = db.query(Permission).filter(
        (Permission.name == permission_data.name) | (Permission.code == permission_data.code)
    ).first()
    if existing_permission:
        raise HTTPException(status_code=400, detail="Permission with this name or code already exists")
    
    permission = Permission(
        **permission_data.dict(),
        created_by=current_user.id
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission

@router.put("/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление разрешения"""
    permission = db.query(Permission).filter(Permission.id == permission_id, Permission.is_active == True).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Проверка уникальности
    if permission_data.name or permission_data.code:
        existing_permission = db.query(Permission).filter(
            ((Permission.name == permission_data.name) & (Permission.id != permission_id)) |
            ((Permission.code == permission_data.code) & (Permission.id != permission_id))
        ).first()
        if existing_permission:
            raise HTTPException(status_code=400, detail="Permission with this name or code already exists")
    
    for field, value in permission_data.dict(exclude_unset=True).items():
        setattr(permission, field, value)
    
    db.commit()
    db.refresh(permission)
    return permission

@router.delete("/{permission_id}")
def delete_permission_hard(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Жесткое удаление разрешения"""
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    db.delete(permission)
    db.commit()
    return {"message": "Permission deleted successfully"}

@router.delete("/{permission_id}/soft")
def delete_permission_soft(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Мягкое удаление разрешения"""
    permission = db.query(Permission).filter(Permission.id == permission_id, Permission.is_active == True).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    permission.is_active = False
    permission.deleted_by = current_user.id
    db.commit()
    return {"message": "Permission soft deleted successfully"}

@router.post("/{permission_id}/restore")
def restore_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Восстановление мягко удаленного разрешения"""
    permission = db.query(Permission).filter(Permission.id == permission_id, Permission.is_active == False).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found or already active")
    
    permission.is_active = True
    permission.deleted_by = None
    db.commit()
    return {"message": "Permission restored successfully"}