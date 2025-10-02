import pytest
from fastapi import HTTPException
from datetime import date  # Добавляем импорт date

from app.auth.permission_service import PermissionService
from tests.test_models import db_session  # Импортируем фикстуру

class TestPermissionService:
    def test_check_permission_no_roles(self, db_session):
        """Тест проверки разрешения у пользователя без ролей"""
        result = PermissionService.check_permission(1, "some_permission", db_session)
        assert result == False

    def test_check_permission_with_role_but_no_permission(self, db_session):
        """Тест проверки разрешения у пользователя с ролью, но без нужного разрешения"""
        from app.models.user import User
        from app.models.role import Role, UserRole, Permission
        
        # Создаем пользователя
        user = User(
            username="TestUser",
            email="test@example.com",
            password_hash="hash",
            birthday=date(2000, 1, 1)  # Используем date
        )
        db_session.add(user)
        
        # Создаем роль
        role = Role(name="Test Role", code="test_role", created_by=1)
        db_session.add(role)
        
        # Создаем разрешение
        permission = Permission(name="Other Permission", code="other_permission", created_by=1)
        db_session.add(permission)
        
        # Связываем пользователя с ролью
        user_role = UserRole(user_id=user.id, role_id=role.id, created_by=1)
        db_session.add(user_role)
        
        db_session.commit()
        
        # Проверяем несуществующее разрешение
        result = PermissionService.check_permission(user.id, "non_existent_permission", db_session)
        assert result == False

    def test_check_permission_with_valid_permission(self, db_session):
        """Тест успешной проверки разрешения"""
        from app.models.user import User
        from app.models.role import Role, UserRole, Permission, RolePermission
        
        # Создаем пользователя
        user = User(
            username="TestUser",
            email="test@example.com",
            password_hash="hash",
            birthday=date(2000, 1, 1)  # Используем date
        )
        db_session.add(user)
        
        # Создаем роль
        role = Role(name="Test Role", code="test_role", created_by=1)
        db_session.add(role)
        
        # Создаем разрешение
        permission = Permission(name="Test Permission", code="test_permission", created_by=1)
        db_session.add(permission)
        
        # Связываем пользователя с ролью
        user_role = UserRole(user_id=user.id, role_id=role.id, created_by=1)
        db_session.add(user_role)
        
        # Связываем роль с разрешением
        role_permission = RolePermission(role_id=role.id, permission_id=permission.id, created_by=1)
        db_session.add(role_permission)
        
        db_session.commit()
        
        # Проверяем существующее разрешение
        result = PermissionService.check_permission(user.id, "test_permission", db_session)
        assert result == True

    def test_require_permission_decorator(self, db_session):
        """Тест декоратора проверки разрешений"""
        from app.auth.permission_service import require_permission
        from app.models.user import User
        
        # Создаем mock пользователя
        user = User(id=1, username="test", email="test@test.com", 
                   password_hash="hash", birthday=date(2000, 1, 1))  # Используем date
        
        # Тестируем случай без разрешения (должен бросить исключение)
        permission_dependency = require_permission("some_permission")
        
        with pytest.raises(HTTPException) as exc_info:
            permission_dependency(current_user=user, db=db_session)
        
        assert exc_info.value.status_code == 403
        assert "Required permission: some_permission" in str(exc_info.value.detail)