from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.user import Base  # Используем существующий Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Связи
    user_roles = relationship("UserRole", back_populates="role")
    role_permissions = relationship("RolePermission", back_populates="role")

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Связи
    role_permissions = relationship("RolePermission", back_populates="permission")

class UserRole(Base):
    __tablename__ = "users_and_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Связи
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

class RolePermission(Base):
    __tablename__ = "roles_and_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Связи
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")