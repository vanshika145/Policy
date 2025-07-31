from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

# User schemas
class UserBase(BaseModel):
    display_name: Optional[str] = None
    email: EmailStr

class UserCreate(UserBase):
    firebase_uid: str

class User(UserBase):
    id: int
    firebase_uid: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Uploaded file schemas
class UploadedFileBase(BaseModel):
    filename: str
    file_type: str

class UploadedFileCreate(UploadedFileBase):
    file_path: str

class UploadedFile(UploadedFileBase):
    id: int
    user_id: int
    upload_time: datetime
    file_path: str
    
    class Config:
        from_attributes = True

# Embeddings schemas
class EmbeddingsStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class EmbeddingsResponse(BaseModel):
    success: bool
    message: str
    file_id: int
    user_id: int
    status: EmbeddingsStatus

# Response schemas
class UploadResponse(BaseModel):
    success: bool
    message: str
    file: UploadedFile
    user: User

class UserInfoResponse(BaseModel):
    firebase_uid: str
    email: str
    display_name: Optional[str]
    created_at: datetime 