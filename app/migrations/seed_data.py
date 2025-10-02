from sqlalchemy.orm import Session
from datetime import date
import sys
import os

# Добавляем путь для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from app.core.database import SessionLocal
from app.models.role import Role, Permission, RolePermission, UserRole
from app.models.user import User
from app.core.security import get_password_hash

def create_initial_roles(db: Session):
    """Создание начальных ролей"""
    print("Создание начальных ролей...")
    
    roles_data = [
        {"name": "Администратор", "code": "admin", "description": "Полный доступ ко всем функциям"},
        {"name": "Пользователь", "code": "user", "description": "Обычный пользователь"},
        {"name": "Гость", "code": "guest", "description": "Ограниченный доступ"}
    ]
    
    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.code == role_data["code"]).first()
        if not existing_role:
            role = Role(
                name=role_data["name"],
                code=role_data["code"],
                description=role_data["description"],
                created_by=1
            )
            db.add(role)
    
    db.commit()
    print("Роли созданы успешно!")

def create_initial_permissions(db: Session):
    """Создание начальных разрешений"""
    print("Создание начальных разрешений...")
    
    entities = ["user", "role", "permission"]
    actions = ["get-list", "read", "create", "update", "delete", "restore"]
    
    permissions_data = []
    
    for entity in entities:
        for action in actions:
            permissions_data.append({
                "name": f"{action.replace('-', ' ').title()} {entity}",
                "code": f"{action}-{entity}",
                "description": f"Разрешение на {action} для {entity}"
            })
    
    # Специальные разрешения
    permissions_data.extend([
        {"name": "Manage User Roles", "code": "manage-user-roles", "description": "Управление ролями пользователей"},
        {"name": "Manage Role Permissions", "code": "manage-role-permissions", "description": "Управление разрешениями ролей"}
    ])
    
    for perm_data in permissions_data:
        existing_perm = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if not existing_perm:
            permission = Permission(
                name=perm_data["name"],
                code=perm_data["code"],
                description=perm_data["description"],
                created_by=1
            )
            db.add(permission)
    
    db.commit()
    print("Разрешения созданы успешно!")

def assign_permissions_to_roles(db: Session):
    """Назначение разрешений ролям"""
    print("Назначение разрешений ролям...")
    
    # Получаем роли
    admin_role = db.query(Role).filter(Role.code == "admin").first()
    user_role = db.query(Role).filter(Role.code == "user").first()
    guest_role = db.query(Role).filter(Role.code == "guest").first()
    
    if not admin_role or not user_role or not guest_role:
        print("Ошибка: не все роли созданы")
        return
    
    # Получаем все разрешения
    all_permissions = db.query(Permission).all()
    
    # Админ получает все разрешения
    for permission in all_permissions:
        existing = db.query(RolePermission).filter(
            RolePermission.role_id == admin_role.id,
            RolePermission.permission_id == permission.id
        ).first()
        if not existing:
            role_perm = RolePermission(
                role_id=admin_role.id,
                permission_id=permission.id,
                created_by=1
            )
            db.add(role_perm)
    
    # Пользователь получает базовые разрешения для пользователей
    user_permissions = db.query(Permission).filter(
        Permission.code.in_(["get-list-user", "read-user", "update-user"])
    ).all()
    
    for permission in user_permissions:
        existing = db.query(RolePermission).filter(
            RolePermission.role_id == user_role.id,
            RolePermission.permission_id == permission.id
        ).first()
        if not existing:
            role_perm = RolePermission(
                role_id=user_role.id,
                permission_id=permission.id,
                created_by=1
            )
            db.add(role_perm)
    
    # Гость получает только получение списка пользователей
    guest_permission = db.query(Permission).filter(Permission.code == "get-list-user").first()
    if guest_permission:
        existing = db.query(RolePermission).filter(
            RolePermission.role_id == guest_role.id,
            RolePermission.permission_id == guest_permission.id
        ).first()
        if not existing:
            role_perm = RolePermission(
                role_id=guest_role.id,
                permission_id=guest_permission.id,
                created_by=1
            )
            db.add(role_perm)
    
    db.commit()
    print("Разрешения назначены ролям успешно!")

def create_admin_user(db: Session):
    """Создание администратора и назначение ему роли"""
    print("Создание администратора...")
    
    # Создаем администратора
    admin_user = db.query(User).filter(User.username == "Admin").first()
    if not admin_user:
        admin_user = User(
            username="Admin",
            email="admin@example.com",
            password_hash=get_password_hash("Admin123!"),
            birthday=date(2000, 1, 1)
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Администратор создан с ID: {admin_user.id}")
    else:
        print(f"Администратор уже существует с ID: {admin_user.id}")
    
    # Назначаем роль администратора
    admin_role = db.query(Role).filter(Role.code == "admin").first()
    if admin_role:
        existing_user_role = db.query(UserRole).filter(
            UserRole.user_id == admin_user.id,
            UserRole.role_id == admin_role.id
        ).first()
        if not existing_user_role:
            user_role = UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id,
                created_by=1
            )
            db.add(user_role)
            db.commit()
            print("Роль администратора назначена успешно!")
        else:
            print("Роль администратора уже назначена")
    else:
        print("Ошибка: роль администратора не найдена")

def run_all_seeds():
    """Запуск всех сидов"""
    db = SessionLocal()
    try:
        create_initial_roles(db)
        create_initial_permissions(db)
        assign_permissions_to_roles(db)
        create_admin_user(db)
        print("Все сиды выполнены успешно!")
    except Exception as e:
        print(f"Ошибка при выполнении сидов: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_all_seeds()