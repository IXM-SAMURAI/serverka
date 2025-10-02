from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.role import UserRole, RolePermission

class PermissionService:
    @staticmethod
    def check_permission(user_id: int, permission_code: str, db: Session):
        """Проверка наличия разрешения у пользователя"""
        user_roles = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.is_active == True
        ).all()
        
        if not user_roles:
            return False
        
        role_ids = [ur.role_id for ur in user_roles]
        
        # Ищем разрешение среди ролей пользователя
        permission_exists = db.query(RolePermission).join(
            RolePermission.role
        ).filter(
            RolePermission.role_id.in_(role_ids),
            RolePermission.is_active == True,
            RolePermission.role.has(is_active=True),
            RolePermission.permission.has(code=permission_code, is_active=True)
        ).first()
        
        return permission_exists is not None

def require_permission(permission_code: str):
    """Декоратор для проверки разрешений"""
    def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not PermissionService.check_permission(current_user.id, permission_code, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required permission: {permission_code}"
            )
        return current_user
    return permission_dependency