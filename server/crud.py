from sqlalchemy.orm import Session
from models import User, UploadedFile
from schemas import UserCreate
from typing import Optional, List
from firebase_auth import get_user_info_from_token

def get_user_by_firebase_uid(db: Session, firebase_uid: str) -> Optional[User]:
    """Get user by Firebase UID"""
    return db.query(User).filter(User.firebase_uid == firebase_uid).first()

def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user"""
    db_user = User(**user_data.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_or_create_user(db: Session, firebase_uid: str, email: str, display_name: Optional[str] = None) -> User:
    """Get existing user or create new one if doesn't exist"""
    user = get_user_by_firebase_uid(db, firebase_uid)
    if user:
        return user
    
    # Create new user
    user_data = UserCreate(
        firebase_uid=firebase_uid,
        email=email,
        display_name=display_name
    )
    return create_user(db, user_data)

def create_uploaded_file(db: Session, user_id: int, filename: str, file_type: str, file_path: str) -> UploadedFile:
    """Create a new uploaded file record"""
    db_file = UploadedFile(
        user_id=user_id,
        filename=filename,
        file_type=file_type,
        file_path=file_path
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_user_files(db: Session, user_id: int) -> List[UploadedFile]:
    """Get all files uploaded by a user"""
    return db.query(UploadedFile).filter(UploadedFile.user_id == user_id).all()

def get_file_by_id(db: Session, file_id: int) -> Optional[UploadedFile]:
    """Get a specific file by ID"""
    return db.query(UploadedFile).filter(UploadedFile.id == file_id).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by database ID"""
    return db.query(User).filter(User.id == user_id).first() 