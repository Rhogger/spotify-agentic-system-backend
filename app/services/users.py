from sqlalchemy.orm import Session

from app.models.user import User


class UserService:
    @staticmethod
    def get(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()
