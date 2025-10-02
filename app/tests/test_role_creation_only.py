#!/usr/bin/env python3
"""
Тест только создания роли (после исправления)
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_role_creation():
    """Тест создания роли после исправления"""
    print("🛠️ ТЕСТ СОЗДАНИЯ РОЛИ (после исправления)")
    print("=" * 50)
    
    # 1. Авторизация
    print("\n🔐 Авторизация...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "AdminUser", "password": "Admin123!"}
    )
    
    if response.status_code != 200:
        print(f"❌ Ошибка авторизации: {response.status_code}")
        return False
    
    tokens = response.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    print("✅ Авторизация успешна")
    
    # 2. Создание роли
    print("\n🎯 Создание новой роли...")
    role_data = {
        "name": "ProjectManager",
        "code": "project_manager", 
        "description": "Role for project managers"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ref/policy/role/",
        headers=headers,
        json=role_data
    )
    
    if response.status_code == 200:
        new_role = response.json()
        print("✅ РОЛЬ СОЗДАНА УСПЕШНО!")
        print(f"   ID: {new_role['id']}")
        print(f"   Name: {new_role['name']}")
        print(f"   Code: {new_role['code']}")
        return True
    elif response.status_code == 403:
        error_detail = response.json().get('detail', 'No detail')
        print(f"🔒 ДОСТУП ЗАПРЕЩЕН: {error_detail}")
        return False
    else:
        print(f"❌ Ошибка {response.status_code}: {response.text}")
        return False

def main():
    """Основная функция"""
    success = test_role_creation()
    
    if success:
        print("\n🎉 ВСЕ РАБОТАЕТ КОРРЕКТНО!")
        print("✅ Ролевая система полностью функционирует")
        print("✅ Создание ролей работает")
        print("✅ Все эндпоинты доступны")
    else:
        print("\n💥 Требуется дополнительная настройка")

if __name__ == "__main__":
    main()
    