from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.auth import AuthService

from app.models.user import User
from app.schemas.user import UserRead


class UserService:
    @staticmethod
    def get(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    async def get_profile(db: Session, user_id: int) -> UserRead:
        user = UserService.get(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        spotify_profile = await AuthService.get_spotify_profile_with_refresh(db, user)

        return UserRead(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            spotify_id=user.spotify_id,
            spotify_access_token=user.spotify_access_token,
            spotify_profile=spotify_profile,
        )
