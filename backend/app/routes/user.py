from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import DEFAULT_USER_ID
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserProfile, UserProfileUpdate

router = APIRouter(prefix="/api/user", tags=["user"])


def _get_or_create_user(db: Session) -> User:
    """Get the configured default user or create one if not exists."""
    user = db.query(User).filter(User.id == DEFAULT_USER_ID).first()
    if not user:
        user = User(id=DEFAULT_USER_ID, name="学生")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("/profile", response_model=UserProfile)
def get_profile(db: Session = Depends(get_db)):
    user = _get_or_create_user(db)
    return user


@router.put("/profile", response_model=UserProfile)
def update_profile(payload: UserProfileUpdate, db: Session = Depends(get_db)):
    user = _get_or_create_user(db)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
