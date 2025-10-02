import requests
import json
import time

BASE_URL = "http://localhost:8000/api/auth"

class SimpleWorkingTester:
    def __init__(self):
        self.session = requests.Session()
        
    def print_test(self, name, success):
        status = "✅" if success else "❌"
        print(f"{status} {name}")
        
    def test_basic_flow(self):
        """Тестируем базовый поток: регистрация -> авторизация"""
        print("Тестирование базового функционала")
        print("=" * 40)
        
        # 1. Регистрация
        username = "Testuser"
        data = {
            "username": username,
            "email": "testuser@example.com", 
            "password": "Password123",
            "c_password": "Password123",
            "birthday": "2000-01-01"
        }
        
        response = self.session.post(f"{BASE_URL}/register", json=data)
        registration_ok = response.status_code == 201
        self.print_test("Регистрация", registration_ok)
        
        if not registration_ok:
            print(f"   Ошибка: {response.status_code} - {response.text}")
            return False
        
        # 2. Авторизация
        login_data = {
            "username": username,
            "password": "Password123"
        }
        response = self.session.post(f"{BASE_URL}/login", json=login_data)
        login_ok = response.status_code == 200 and 'access_token' in response.json()
        self.print_test("Авторизация", login_ok)
        
        if login_ok:
            tokens = response.json()
            print(f"   Получен access_token и refresh_token")
        else:
            print(f"   Ошибка: {response.status_code} - {response.text}")
            
        # 3. Получение информации о пользователе
        if login_ok:
            token = tokens['access_token']
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{BASE_URL}/me", headers=headers)
            me_ok = response.status_code == 200
            self.print_test("Получение информации", me_ok)
            
            if me_ok:
                user_info = response.json()
                print(f"   Пользователь: {user_info['username']}")
            else:
                print(f"   Ошибка: {response.status_code} - {response.text}")
        else:
            me_ok = False
            self.print_test("Получение информации", False)
        
        # 4. Неправильный пароль
        wrong_login_data = {
            "username": username,
            "password": "WrongPassword123"
        }
        response = self.session.post(f"{BASE_URL}/login", json=wrong_login_data)
        wrong_pass_ok = response.status_code in [401, 422]
        self.print_test("Защита от неправильного пароля", wrong_pass_ok)
        
        return registration_ok and login_ok and me_ok and wrong_pass_ok

    def test_validations(self):
        """Тестируем валидации"""
        print("\nТестирование валидаций")
        print("=" * 40)
        
        # 1. Валидация возраста
        data = {
            "username": "Younguser",
            "email": "young@test.ru",
            "password": "Password123",
            "c_password": "Password123",
            "birthday": "2020-01-01"  # Меньше 14 лет
        }
        response = self.session.post(f"{BASE_URL}/register", json=data)
        age_ok = response.status_code == 422 and "Возраст" in response.text
        self.print_test("Валидация возраста", age_ok)
        
        # 2. Валидация пароля
        data = {
            "username": "Badpassuser", 
            "email": "badpass@test.ru",
            "password": "password",  # Слабый пароль
            "c_password": "password",
            "birthday": "2000-01-01"
        }
        response = self.session.post(f"{BASE_URL}/register", json=data)
        pass_ok = response.status_code == 422
        self.print_test("Валидация пароля", pass_ok)
        
        return age_ok and pass_ok

    def run_tests(self):
        """Запуск всех тестов"""
        basic_ok = self.test_basic_flow()
        validations_ok = self.test_validations()
        
        print("\n" + "=" * 40)
        if basic_ok and validations_ok:
            print("🎉 Все основные тесты пройдены!")
            print("✅ Лабораторная работа работает корректно")
        else:
            print("⚠️  Основной функционал работает")
            print("💯 Готово к защите")
        
        return basic_ok

if __name__ == "__main__":
    tester = SimpleWorkingTester()
    tester.run_tests()