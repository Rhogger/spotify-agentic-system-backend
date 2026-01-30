from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserRead
from app.services.users import UserService

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def read_users_me(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Retorna os dados do usuário atual autenticado e seu perfil no Spotify.
    """
    return await UserService.get_profile(db, current_user.id)
