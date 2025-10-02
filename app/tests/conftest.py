import pytest
import os
import sys

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Настройка тестового окружения"""
    # Устанавливаем тестовую БД
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    yield
    # Очистка после тестов
    if os.path.exists("test.db"):
        os.remove("test.db")