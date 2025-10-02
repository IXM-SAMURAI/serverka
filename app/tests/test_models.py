import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date

from app.models.user import Base as UserBase, User, Token
from app.models.role import Base as RoleBase, Role, Permission, UserRole, RolePermission
from app.core.security import get_password_hash

# Тестовая БД
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Создание тестовой сессии БД"""
    # Создаем таблицы
    UserBase.metadata.create_all(bind=engine)
    RoleBase.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Очищаем таблицы после теста
        UserBase.metadata.drop_all(bind=engine)
        RoleBase.metadata.drop_all(bind=engine)

class TestUserModel:
    def test_create_user(self, db_session):
        """Тест создания пользователя"""
        user = User(
            username="TestUser",
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            birthday=date(2000, 1, 1)
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "TestUser"
        assert user.is_active == True

class TestRoleModels:
    def test_create_role(self, db_session):
        """Тест создания роли"""
        role = Role(
            name="Test Role",
            code="test_role",
            description="Test role description",
            created_by=1
        )
        db_session.add(role)
        db_session.commit()
        
        assert role.id is not None
        assert role.code == "test_role"
        assert role.is_active == True

    def test_create_permission(self, db_session):
        """Тест создания разрешения"""
        permission = Permission(
            name="Test Permission",
            code="test_permission",
            description="Test permission description",
            created_by=1
        )
        db_session.add(permission)
        db_session.commit()
        
        assert permission.id is not None
        assert permission.code == "test_permission"

    def test_user_role_relationship(self, db_session):
        """Тест связи пользователь-роль"""
        # Создаем пользователя
        user = User(
            username="TestUser",
            email="test@example.com",
            password_hash=get_password_hash("password123"),
            birthday=date(2000, 1, 1)
        )
        db_session.add(user)
        db_session.commit()
        
        # Создаем роль
        role = Role(
            name="Test Role",
            code="test_role",
            created_by=1
        )
        db_session.add(role)
        db_session.commit()
        
        # Создаем связь
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
            created_by=1
        )
        db_session.add(user_role)
        db_session.commit()
        
        # Проверяем связи
        assert user_role.user_id == user.id
        assert user_role.role_id == role.id
        assert user_role.is_active == True
        
        # Проверяем обратные связи
        assert user.user_roles[0].id == user_role.id
        assert role.user_roles[0].id == user_role.id

    def test_role_permission_relationship(self, db_session):
        """Тест связи роль-разрешение"""
        # Создаем роль
        role = Role(
            name="Test Role",
            code="test_role",
            created_by=1
        )
        db_session.add(role)
        
        # Создаем разрешение
        permission = Permission(
            name="Test Permission",
            code="test_permission",
            created_by=1
        )
        db_session.add(permission)
        db_session.commit()
        
        # Создаем связь
        role_permission = RolePermission(
            role_id=role.id,
            permission_id=permission.id,
            created_by=1
        )
        db_session.add(role_permission)
        db_session.commit()
        
        # Проверяем связи
        assert role_permission.role_id == role.id
        assert role_permission.permission_id == permission.id
        
        # Проверяем обратные связи
        assert role.role_permissions[0].id == role_permission.id
        assert permission.role_permissions[0].id == role_permission.id