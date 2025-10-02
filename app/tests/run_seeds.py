#!/usr/bin/env python3
"""
Скрипт для выполнения миграций из корневой директории
"""

import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.migrations.seed_data import run_all_seeds
from app.core.database import create_tables

if __name__ == "__main__":
    print("Запуск создания таблиц и сидов...")
    
    # Создаем таблицы
    create_tables()
    
    # Заполняем начальными данными
    run_all_seeds()
    
    print("Миграции завершены успешно!")