import pytest
from fastapi.testclient import TestClient
from datetime import date

from main import app
from app.core.security import create_access_token
from tests.test_models import db_session, engine
from app.models.user import Base as UserBase, User
from app.models.role import Base as RoleBase, Role, Permission, UserRole, RolePermission

client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    """Фикстура для тестовой БД"""
    UserBase.metadata.create_all(bind=engine)
    RoleBase.metadata.create_all(bind=engine)
    yield
    UserBase.metadata.drop_all(bind=engine)
    RoleBase.metadata.drop_all(bind=engine)

class TestRoleRoutes:
    def test_get_roles_unauthorized(self, test_db):
        """Тест получения ролей без авторизации"""
        response = client.get("/api/ref/policy/role/")
        assert response.status_code == 401

    def test_create_role_authorized(self, test_db, db_session):
        """Тест создания роли с авторизацией"""
        # Создаем тестового пользователя
        user = User(
            username="TestUser",
            email="test@example.com",
            password_hash="hash",
            birthday=date(2000, 1, 1)
        )
        db_session.add(user)
        db_session.commit()
        
        # Создаем токен
        token = create_access_token({"sub": str(user.id), "username": user.username})
        
        # Создаем роль
        role_data = {
            "name": "Test Role",
            "code": "test_role",
            "description": "Test description"
        }
        
        response = client.post(
            "/api/ref/policy/role/",
            json=role_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Role"
        assert data["code"] == "test_role"

    def test_create_duplicate_role(self, test_db, db_session):
        """Тест создания дублирующейся роли"""
        user = User(
            username="TestUser",
            email="test@example.com",
            password_hash="hash",
            birthday=date(2000, 1, 1)
        )
        db_session.add(user)
        
        # Создаем существующую роль
        existing_role = Role(name="Existing Role", code="existing_role", created_by=1)
        db_session.add(existing_role)
        db_session.commit()
        
        token = create_access_token({"sub": str(user.id), "username": user.username})
        
        # Пытаемся создать роль с тем же кодом
        role_data = {
            "name": "New Role",
            "code": "existing_role",  # Дублирующий код
            "description": "Test description"
        }
        
        response = client.post(
            "/api/ref/policy/role/",
            json=role_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

class TestPermissionRoutes:
    def test_get_permissions_authorized(self, test_db, db_session):
        """Тест получения разрешений с авторизацией"""
        user = User(
            username="TestUser",
            email="test@example.com",
            password_hash="hash",
            birthday=date(2000, 1, 1)
        )
        db_session.add(user)
        db_session.commit()
        
        token = create_access_token({"sub": str(user.id), "username": user.username})
        
        response = client.get(
            "/api/ref/policy/permission/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)

class TestUserRoleRoutes:
    def test_assign_role_to_user(self, test_db, db_session):
        """Тест назначения роли пользователю"""
        # Создаем пользователя
        user = User(
            username="TestUser",
            email="test@example.com",
            password_hash="hash",
            birthday=date(2000, 1, 1)
        )
        db_session.add(user)
        
        # Создаем роль
        role = Role(name="Test Role", code="test_role", created_by=1)
        db_session.add(role)
        db_session.commit()
        
        token = create_access_token({"sub": str(user.id), "username": user.username})
        
        # Назначаем роль
        role_data = {"role_id": role.id}
        
        response = client.post(
            f"/api/ref/user/{user.id}/role",
            json=role_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert data["role_id"] == role.id

    def test_get_user_roles(self, test_db, db_session):
        """Тест получения ролей пользователя"""
        user = User(
            username="TestUser",
            email="test@example.com",
            password_hash="hash",
            birthday=date(2000, 1, 1)
        )
        db_session.add(user)
        
        role = Role(name="Test Role", code="test_role", created_by=1)
        db_session.add(role)
        db_session.commit()
        
        # Назначаем роль
        user_role = UserRole(user_id=user.id, role_id=role.id, created_by=1)
        db_session.add(user_role)
        db_session.commit()
        
        token = create_access_token({"sub": str(user.id), "username": user.username})
        
        response = client.get(
            f"/api/ref/user/{user.id}/role",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["role_id"] == role.id