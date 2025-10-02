from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Настройка базы данных
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Создание таблиц в БД"""
    from app.models.user import Base
    from app.models.role import Base as RoleBase
    
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы успешно!")

def get_db():
    """Зависимость для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()