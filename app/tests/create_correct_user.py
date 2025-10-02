#!/usr/bin/env python3
"""
Создание правильного пользователя через API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_proper_admin():
    """Создание правильного администратора"""
    print("👤 СОЗДАНИЕ ПРАВИЛЬНОГО АДМИНИСТРАТОРА")
    print("-" * 50)
    
    # Правильные данные (проходят валидацию)
    user_data = {
        "username": "AdminUser",      # 8 символов
        "email": "adminuser@example.com",
        "password": "Admin123!",      # 8+ символов, цифры, буквы разного регистра
        "c_password": "Admin123!",
        "birthday": "2000-01-01"      # Возраст > 14 лет
    }
    
    print("📤 Регистрируем пользователя...")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=user_data
    )
    
    if response.status_code == 201:
        user = response.json()
        print("✅ ПОЛЬЗОВАТЕЛЬ СОЗДАН!")
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
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data
    )
    
    if response.status_code == 200:
        tokens = response.json()
        print("✅ АВТОРИЗАЦИЯ УСПЕШНА!")
        print(f"   Access Token: {tokens['access_token'][:30]}...")
        return tokens
    else:
        print(f"❌ ОШИБКА: {response.status_code}")
        print(f"   Ответ: {response.text}")
        return None

def test_protected_endpoints(access_token):
    """Тест защищенных эндпоинтов"""
    print("\n🔒 ТЕСТ ЗАЩИЩЕННЫХ ЭНДПОИНТОВ")
    print("-" * 40)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    endpoints = [
        ("/auth/me", "Информация о пользователе"),
        ("/api/ref/policy/role/", "Список ролей"),
        ("/api/ref/policy/permission/", "Список разрешений"),
        ("/api/ref/user/2/role", "Роли пользователя (ID: 2)"),
    ]
    
    for endpoint, description in endpoints:
        print(f"\n📡 {description}")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   ✅ Успешно! Записей: {len(data)}")
            else:
                print(f"   ✅ Успешно!")
                if 'username' in data:
                    print(f"     👤 Пользователь: {data['username']}")
        elif response.status_code == 403:
            print(f"   🔒 Доступ запрещен")
        elif response.status_code == 401:
            print(f"   🔐 Не авторизован")
        else:
            print(f"   ❌ Ошибка {response.status_code}")

def test_role_creation(access_token):
    """Тест создания роли"""
    print("\n🛠️ ТЕСТ СОЗДАНИЯ РОЛИ")
    print("-" * 40)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    role_data = {
        "name": "TestManager",
        "code": "test_manager",
        "description": "Test manager role"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ref/policy/role/",
        headers=headers,
        json=role_data
    )
    
    if response.status_code == 200:
        role = response.json()
        print("✅ РОЛЬ СОЗДАНА УСПЕШНО!")
        print(f"   Name: {role['name']}")
        print(f"   Code: {role['code']}")
        print(f"   ID: {role['id']}")
    elif response.status_code == 403:
        error_detail = response.json().get('detail', 'No detail')
        print(f"🔒 ДОСТУП ЗАПРЕЩЕН: {error_detail}")
    else:
        print(f"❌ ОШИБКА {response.status_code}: {response.text}")

def main():
    """Основная функция"""
    print("🎯 СОЗДАНИЕ РАБОЧЕГО ПОЛЬЗОВАТЕЛЯ ДЛЯ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    # Создаем пользователя
    user = create_proper_admin()
    if not user:
        print("\n💡 Попробуйте создать пользователя через документацию:")
        print("   http://localhost:8000/docs")
        print("   Используйте данные:")
        print('   {"username": "AdminUser", "email": "admin@test.com", "password": "Admin123!", "c_password": "Admin123!", "birthday": "2000-01-01"}')
        return
    
    # Тестируем авторизацию
    tokens = test_login("AdminUser", "Admin123!")
    if not tokens:
        return
    
    # Тестируем защищенные эндпоинты
    test_protected_endpoints(tokens['access_token'])
    
    # Тестируем создание роли
    test_role_creation(tokens['access_token'])
    
    print("\n🎉 СИСТЕМА ГОТОВА К РАБОТЕ!")
    print("\n🔑 ДЛЯ ТЕСТИРОВАНИЯ ИСПОЛЬЗУЙТЕ:")
    print("   Username: AdminUser")
    print("   Password: Admin123!")

if __name__ == "__main__":
    main()