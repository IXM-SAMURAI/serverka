import pytest
from app.migrations.seed_data import (
    create_initial_roles,
    create_initial_permissions,
    assign_permissions_to_roles,
    create_admin_user
)
from tests.test_models import db_session
from app.models.role import Role, Permission, RolePermission, UserRole  # Добавляем импорты
from app.models.user import User  # Добавляем импорт

class TestMigrations:
    def test_create_initial_roles(self, db_session):
        """Тест создания начальных ролей"""
        create_initial_roles(db_session)
        
        roles = db_session.query(Role).all()
        role_codes = [role.code for role in roles]
        
        assert "admin" in role_codes
        assert "user" in role_codes
        assert "guest" in role_codes
        assert len(roles) == 3

    def test_create_initial_permissions(self, db_session):
        """Тест создания начальных разрешений"""
        create_initial_permissions(db_session)
        
        permissions = db_session.query(Permission).all()
        permission_codes = [perm.code for perm in permissions]
        
        # Проверяем базовые разрешения
        expected_permissions = [
            "get-list-user", "read-user", "create-user", "update-user", "delete-user", "restore-user",
            "get-list-role", "read-role", "create-role", "update-role", "delete-role", "restore-role",
            "get-list-permission", "read-permission", "create-permission", "update-permission", "delete-permission", "restore-permission",
            "manage-user-roles", "manage-role-permissions"
        ]
        
        for expected_perm in expected_permissions:
            assert expected_perm in permission_codes

    def test_assign_permissions_to_roles(self, db_session):
        """Тест назначения разрешений ролям"""
        # Сначала создаем роли и разрешения
        create_initial_roles(db_session)
        create_initial_permissions(db_session)
        
        # Назначаем разрешения
        assign_permissions_to_roles(db_session)
        
        # Проверяем, что у админа есть разрешения
        admin_role = db_session.query(Role).filter(Role.code == "admin").first()
        admin_permissions = db_session.query(RolePermission).filter(
            RolePermission.role_id == admin_role.id
        ).count()
        
        assert admin_permissions > 0

    def test_create_admin_user(self, db_session):
        """Тест создания администратора"""
        # Сначала создаем роль админа
        admin_role = Role(name="Администратор", code="admin", description="Полный доступ", created_by=1)
        db_session.add(admin_role)
        db_session.commit()
        
        create_admin_user(db_session)
        
        # Проверяем, что пользователь создан
        admin_user = db_session.query(User).filter(User.username == "Admin").first()
        assert admin_user is not None
        assert admin_user.email == "admin@example.com"
        
        # Проверяем, что роль назначена
        user_role = db_session.query(UserRole).filter(
            UserRole.user_id == admin_user.id,
            UserRole.role_id == admin_role.id
        ).first()
        assert user_role is not None