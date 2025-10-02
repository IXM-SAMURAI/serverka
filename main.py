from fastapi import FastAPI
from app.core.database import create_tables

# Создаем таблицы при запуске
create_tables()

app = FastAPI(
    title="Role-Based API", 
    version="1.0.0",
    description="API с ролевой системой авторизации"
)

# Импортируем роутеры - используем правильный auth router из app/auth/
from app.auth.router import router as auth_router
from app.routers.roles import router as roles_router
from app.routers.permissions import router as permissions_router
from app.routers.user_roles import router as user_roles_router

# Регистрируем роутеры
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(roles_router, tags=["roles"])
app.include_router(permissions_router, tags=["permissions"])
app.include_router(user_roles_router, tags=["user-roles"])

@app.get("/")
def read_root():
    return {"message": "Role-Based API with RBAC is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is working correctly"}

@app.get("/test")
def test_endpoint():
    return {"message": "Test endpoint is working!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)