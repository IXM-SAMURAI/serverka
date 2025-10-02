from fastapi import APIRouter

router = APIRouter(prefix="/api/ref/user", tags=["user-roles"])

@router.get("/{user_id}/role")
def get_user_roles(user_id: int):
    return {"message": f"User roles router works for user {user_id}"}