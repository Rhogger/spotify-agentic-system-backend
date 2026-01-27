from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.track_interaction import InteractionTypeEnum, InteractionResponse
from app.services.track_actions import TrackActionsService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/{track_id}/action", response_model=InteractionResponse)
def register_track_action(
    track_id: int,
    type: InteractionTypeEnum,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Registra uma interação do usuário com uma faixa (Like, Skip, etc).
    Requer autenticação.
    """
    return TrackActionsService.register_action(db, current_user, track_id, type)
