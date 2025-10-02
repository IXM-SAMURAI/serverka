#!/usr/bin/env python3
"""
Скрипт для выполнения миграций ролевой системы
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.migrations.init_tables import create_role_tables
from app.migrations.seed_data import run_all_seeds

if __name__ == "__main__":
    print("Запуск миграций ролевой системы...")
    
    # Создаем таблицы
    create_role_tables()
    
    # Заполняем начальными данными
    run_all_seeds()
    
    print("Миграции завершены успешно!")