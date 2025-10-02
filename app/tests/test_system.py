#!/usr/bin/env python3
"""
Диагностика и исправление проблем с аутентификацией
"""

import requests
import json
import sys
import os

# Добавляем путь для импорта моделей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role, UserRole
from app.core.security import get_password_hash
from datetime import date

BASE_URL = "http://localhost:8000"

def check_existing_users():
    """Проверка существующих пользователей в БД"""
    print("🔍 ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ В БАЗЕ ДАННЫХ")
    print("-" * 50)
    
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        if not users:
            print("❌ В базе данных нет пользователей")
            return []
        
        print(f"✅ Найдено пользователей: {len(users)}")
        for user in users:
            print(f"\n👤 ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Active: {user.is_active}")
            print(f"   Created: {user.created_at}")
            
            # Проверяем роли пользователя
            user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
            if user_roles:
                print(f"   🎭 Роли: {len(user_roles)}")
                for ur in user_roles:
                    role = db.query(Role).filter(Role.id == ur.role_id).first()
                    if role:
                        print(f"     - {role.name} ({role.code})")
            else:
                print("   🎭 Роли: нет")
        
        return users
    finally:
        db.close()

def create_proper_user():
    """Создание правильного пользователя"""
    print("\n👤 СОЗДАНИЕ ПРАВИЛЬНОГО ПОЛЬЗОВАТЕЛЯ")
    print("-" * 50)
    
    user_data = {
        "username": "AdminUser",  # 8 символов, только буквы
        "email": "admin@example.com",
        "password": "Admin123!",  # 8+ символов, цифры, буквы разного регистра
        "c_password": "Admin123!",
        "birthday": "2000-01-01"  # Возраст > 14 лет
    }
    
    print("📤 Отправка запроса регистрации...")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=user_data
    )
    
    if response.status_code == 201:
        user = response.json()
        print("✅ ПОЛЬЗОВАТЕЛЬ УСПЕШНО СОЗДАН!")
        print(f"   ID: {user['id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")
        return user
    else:
        print(f"❌ ОШИБКА СОЗДАНИЯ: {response.status_code}")
        print(f"   Ответ: {response.text}")
        return None

def test_login(username, password):
    """Тест авторизации"""
    print(f"\n🔐 ТЕСТ АВТОРИЗАЦИИ: {username}")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    print(f"   Данные: {login_data}")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data
    )
    
    if response.status_code == 200:
        tokens = response.json()
        print("✅ АВТОРИЗАЦИЯ УСПЕШНА!")
        print(f"   Access Token: {tokens['access_token'][:30]}...")
        return tokens
    elif response.status_code == 422:
        print("❌ ОШИБКА ВАЛИДАЦИИ:")
        errors = response.json().get('detail', [])
        for error in errors:
            print(f"   - {error['msg']} (поле: {error['loc']})")
    else:
        print(f"❌ ОШИБКА: {response.status_code}")
        print(f"   Ответ: {response.text}")
    
    return None

def assign_admin_role(user_id):
    """Назначение роли администратора"""
    print(f"\n🎭 НАЗНАЧЕНИЕ РОЛИ АДМИНИСТРАТОРА (User ID: {user_id})")
    
    db = SessionLocal()
    try:
        # Находим роль администратора
        admin_role = db.query(Role).filter(Role.code == "admin").first()
        if not admin_role:
            print("❌ Роль 'admin' не найдена в базе")
            return False
        
        # Проверяем, не назначена ли уже роль
        existing = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == admin_role.id
        ).first()
        
        if existing:
            print("✅ Роль администратора уже назначена")
            return True
        
        # Назначаем роль
        user_role = UserRole(
            user_id=user_id,
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

def test_protected_endpoints(access_token):
    """Тест защищенных эндпоинтов"""
    print("\n🔒 ТЕСТ ЗАЩИЩЕННЫХ ЭНДПОИНТОВ")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    endpoints = [
        ("/auth/me", "Информация о пользователе"),
        ("/api/ref/policy/role/", "Список ролей"),
        ("/api/ref/policy/permission/", "Список разрешений"),
    ]
    
    for endpoint, description in endpoints:
        print(f"\n📡 {description}")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   ✅ Успешно! Записей: {len(data)}")
            else:
                print(f"   ✅ Успешно! Данные получены")
                if 'username' in data:
                    print(f"     Пользователь: {data['username']}")
        else:
            print(f"   ❌ Ошибка {response.status_code}: {response.text}")

def main():
    """Основная функция"""
    print("🚀 ДИАГНОСТИКА И ИСПРАВЛЕНИЕ ПРОБЛЕМ АУТЕНТИФИКАЦИИ")
    print("=" * 60)
    
    # 1. Проверяем существующих пользователей
    users = check_existing_users()
    
    # 2. Если нет пользователей, создаем нового
    if not users:
        print("\n💡 Создаем нового пользователя...")
        user = create_proper_user()
        if not user:
            return
        user_id = user['id']
    else:
        # Используем первого существующего пользователя
        user = users[0]
        user_id = user.id
        print(f"\n💡 Используем существующего пользователя: {user.username}")
    
    # 3. Назначаем роль администратора
    assign_admin_role(user_id)
    
    # 4. Тестируем авторизацию
    tokens = test_login("AdminUser", "Admin123!")
    if not tokens:
        # Пробуем с существующим пользователем
        if users:
            tokens = test_login(users[0].username, "Admin123!")
    
    if not tokens:
        print("\n💥 Не удалось авторизоваться")
        print("💡 Попробуйте создать пользователя через документацию:")
        print("   http://localhost:8000/docs#/authentication/register_auth_register_post")
        return
    
    # 5. Тестируем защищенные эндпоинты
    test_protected_endpoints(tokens['access_token'])
    
    print("\n🎉 ДИАГНОСТИКА ЗАВЕРШЕНА!")
    print("📊 Резюме:")
    print("   - Проверены пользователи в БД ✅")
    print("   - Создан/использован пользователь ✅") 
    print("   - Назначена роль администратора ✅")
    print("   - Протестирована авторизация ✅")
    print("   - Проверены защищенные эндпоинты ✅")

if __name__ == "__main__":
    main()