#!/usr/bin/env python3
"""
Скрипт для запуска тестов
"""

import subprocess
import sys

def run_tests():
    """Запуск всех тестов"""
    print("Запуск тестов ролевой системы...")
    
    # Запускаем pytest
    result = subprocess.run([
        "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "--cov=app",
        "--cov-report=html"
    ], capture_output=False)
    
    if result.returncode == 0:
        print("✅ Все тесты прошли успешно!")
    else:
        print("❌ Некоторые тесты не прошли")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()