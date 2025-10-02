from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class RoleBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    created_by: int
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    is_active: bool
    
    class Config:
        from_attributes = True

class PermissionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    created_by: int
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    is_active: bool
    
    class Config:
        from_attributes = True

class UserRoleBase(BaseModel):
    user_id: int
    role_id: int

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleResponse(UserRoleBase):
    id: int
    created_at: datetime
    created_by: int
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    is_active: bool
    
    class Config:
        from_attributes = True

class RolePermissionBase(BaseModel):
    role_id: int
    permission_id: int

class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermissionResponse(RolePermissionBase):
    id: int
    created_at: datetime
    created_by: int
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    is_active: bool
    
    class Config:
        from_attributes = True