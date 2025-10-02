from app.core.database import engine
from app.models.user import Base as UserBase
from app.models.role import Base as RoleBase

def create_role_tables():
    """Создание таблиц для ролевой системы"""
    print("Создание таблиц ролевой системы...")
    
    # Создаем таблицы для ролей и разрешений
    RoleBase.metadata.create_all(bind=engine)
    
    print("Таблицы ролевой системы созданы успешно!")
    print("- roles")
    print("- permissions") 
    print("- users_and_roles")
    print("- roles_and_permissions")

if __name__ == "__main__":
    create_role_tables()