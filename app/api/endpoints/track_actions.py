from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.track_interaction import InteractionTypeEnum, InteractionResponse
from app.services.track_actions import TrackActionsService
from app.api.deps import get_current_user
from app.models.user import User

from app.core.logger import logger

router = APIRouter()


@router.post(
    "/{track_id}/action",
    response_model=InteractionResponse,
    summary="Registra interação com faixa",
    description="Registra uma ação do usuário com uma música, como curtir (Like), pular (Skip), ou outras interações. Requer autenticação.",
)
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
    logger.info(
        f"Recebendo requisição de ação {type} para faixa {track_id} do usuário {current_user.id}"
    )
    return TrackActionsService.register_action(db, current_user, track_id, type)
