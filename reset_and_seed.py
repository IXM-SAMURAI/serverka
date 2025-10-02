#!/usr/bin/env python3
"""
Пересоздание БД и заполнение начальными данными
"""

import os
import sys

def reset_database():
    """Пересоздание базы данных"""
    print("🗑️  ПЕРЕСОЗДАНИЕ БАЗЫ ДАННЫХ")
    print("-" * 40)
    
    # Удаляем старую БД
    if os.path.exists("app.db"):
        os.remove("app.db")
        print("✅ Старая БД удалена")
    else:
        print("ℹ️  Файл БД не найден, создаем новый")
    
    # Импортируем и создаем таблицы
    from app.core.database import create_tables
    create_tables()
    print("✅ Таблицы созданы")

def run_seeds():
    """Запуск сидов"""
    print("\n🌱 ЗАПУСК НАЧАЛЬНЫХ ДАННЫХ")
    print("-" * 40)
    
    from app.migrations.seed_data import run_all_seeds
    run_all_seeds()
    print("✅ Начальные данные загружены")

def verify_data():
    """Проверка данных"""
    print("\n🔍 ПРОВЕРКА ДАННЫХ")
    print("-" * 40)
    
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.models.role import Role, Permission, UserRole
    
    db = SessionLocal()
    try:
        # Проверяем пользователей
        users = db.query(User).all()
        print(f"👤 Пользователей: {len(users)}")
        for user in users:
            print(f"   - {user.username} (ID: {user.id})")
        
        # Проверяем роли
        roles = db.query(Role).all()
        print(f"🎭 Ролей: {len(roles)}")
        for role in roles:
            print(f"   - {role.name} ({role.code})")
        
        # Проверяем разрешения
        permissions = db.query(Permission).all()
        print(f"🔑 Разрешений: {len(permissions)}")
        
        # Проверяем связи пользователь-роль
        user_roles = db.query(UserRole).all()
        print(f"🔗 Связей пользователь-роль: {len(user_roles)}")
        for ur in user_roles:
            user = db.query(User).filter(User.id == ur.user_id).first()
            role = db.query(Role).filter(Role.id == ur.role_id).first()
            if user and role:
                print(f"   - {user.username} -> {role.name}")
        
    finally:
        db.close()

def main():
    """Основная функция"""
    print("🚀 ПЕРЕСОЗДАНИЕ И НАСТРОЙКА БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    # Пересоздаем БД
    reset_database()
    
    # Запускаем сиды
    run_seeds()
    
    # Проверяем данные
    verify_data()
    
    print("\n🎉 БАЗА ДАННЫХ ГОТОВА К РАБОТЕ!")
    print("\n🔑 ДЛЯ ТЕСТИРОВАНИЯ ИСПОЛЬЗУЙТЕ:")
    print("   Username: Admin")
    print("   Password: Admin123!")

if __name__ == "__main__":
    main()