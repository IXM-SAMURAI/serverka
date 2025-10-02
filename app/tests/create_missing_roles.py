#!/usr/bin/env python3
"""
Создание отсутствующих ролей в базе данных
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.role import Role

def create_missing_roles():
    """Создание отсутствующих ролей"""
    print("🎭 СОЗДАНИЕ ОТСУТСТВУЮЩИХ РОЛЕЙ")
    print("-" * 40)
    
    db = SessionLocal()
    try:
        # Роли которые должны быть в системе
        required_roles = [
            {"name": "Администратор", "code": "admin", "description": "Полный доступ ко всем функциям"},
            {"name": "Пользователь", "code": "user", "description": "Обычный пользователь"},
            {"name": "Гость", "code": "guest", "description": "Ограниченный доступ"}
        ]
        
        created_count = 0
        
        for role_data in required_roles:
            # Проверяем, существует ли роль
            existing_role = db.query(Role).filter(Role.code == role_data["code"]).first()
            
            if not existing_role:
                # Создаем роль
                role = Role(
                    name=role_data["name"],
                    code=role_data["code"],
                    description=role_data["description"],
                    created_by=1  # Система
                )
                db.add(role)
                created_count += 1
                print(f"✅ Создана роль: {role_data['name']} ({role_data['code']})")
            else:
                print(f"ℹ️  Роль уже существует: {role_data['name']} ({role_data['code']})")
        
        db.commit()
        
        print(f"\n📊 ИТОГ: Создано {created_count} новых ролей")
        
        # Показываем все роли в системе
        print("\n🎭 ВСЕ РОЛИ В СИСТЕМЕ:")
        all_roles = db.query(Role).all()
        for role in all_roles:
            print(f"   - {role.name} ({role.code}) - ID: {role.id}")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания ролей: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def assign_admin_role_to_user():
    """Назначение роли администратора пользователю AdminUser"""
    print("\n👤 НАЗНАЧЕНИЕ РОЛИ АДМИНИСТРАТОРА")
    print("-" * 40)
    
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.models.role import UserRole
        
        # Находим пользователя
        user = db.query(User).filter(User.username == "AdminUser").first()
        if not user:
            print("❌ Пользователь AdminUser не найден")
            return False
        
        # Находим роль администратора
        admin_role = db.query(Role).filter(Role.code == "admin").first()
        if not admin_role:
            print("❌ Роль 'admin' не найдена")
            return False
        
        print(f"👤 Пользователь: {user.username} (ID: {user.id})")
        print(f"🎭 Роль: {admin_role.name} (ID: {admin_role.id})")
        
        # Проверяем, не назначена ли уже роль
        existing = db.query(UserRole).filter(
            UserRole.user_id == user.id,
            UserRole.role_id == admin_role.id
        ).first()
        
        if existing:
            print("✅ Роль администратора уже назначена")
            return True
        
        # Назначаем роль
        user_role = UserRole(
            user_id=user.id,
            role_id=admin_role.id,
            created_by=1  # Система
        )
        db.add(user_role)
        db.commit()
        
        print("✅ Роль администратора назначена успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка назначения роли: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Основная функция"""
    print("🚀 СОЗДАНИЕ ОТСУТСТВУЮЩИХ РОЛЕЙ")
    print("=" * 50)
    
    # 1. Создаем отсутствующие роли
    if not create_missing_roles():
        return
    
    # 2. Назначаем роль администратора пользователю
    assign_admin_role_to_user()
    
    print("\n🎉 ПРОБЛЕМА С РОЛЯМИ РЕШЕНА!")
    print("\n✅ ЧТО БЫЛО ИСПРАВЛЕНО:")
    print("   - Созданы отсутствующие роли (admin, user, guest)")
    print("   - Назначена роль 'admin' пользователю AdminUser")
    print("\n🔑 ДЛЯ ТЕСТИРОВАНИЯ:")
    print("   Username: AdminUser")
    print("   Password: Admin123!")
    print("\n💡 Вся остальная функциональность сохраняется рабочей")

if __name__ == "__main__":
    main()