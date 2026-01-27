from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.track import Track
from app.models.track_preference import TrackPreference
from app.models.track_behavior import TrackBehavior, InteractionType
from app.schemas.track_interaction import InteractionTypeEnum, InteractionResponse
from app.models.user import User


class TrackActionsService:
    @staticmethod
    def register_action(
        db: Session, user: User, track_id: int, action_type: InteractionTypeEnum
    ) -> InteractionResponse:
        """
        Registra uma ação do usuário sobre uma música (Like, Dislike, Skip, Back, View).
        """
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            raise HTTPException(
                status_code=404, detail="Música não encontrada no catálogo"
            )

        message = ""

        if action_type in [InteractionTypeEnum.LIKE, InteractionTypeEnum.DISLIKE]:
            is_liked = action_type == InteractionTypeEnum.LIKE

            pref = (
                db.query(TrackPreference)
                .filter_by(user_id=user.id, track_id=track_id)
                .first()
            )

            if pref:
                pref.liked = is_liked
            else:
                new_pref = TrackPreference(
                    user_id=user.id, track_id=track_id, liked=is_liked
                )
                db.add(new_pref)

            message = f"Preferência '{action_type}' registada com sucesso."

        else:
            interaction_enum_map = {
                InteractionTypeEnum.SKIP: InteractionType.SKIP,
                InteractionTypeEnum.BACK: InteractionType.BACK,
                InteractionTypeEnum.VIEW: InteractionType.VIEW,
            }

            if action_type not in interaction_enum_map:
                raise HTTPException(
                    status_code=400,
                    detail="Tipo de interação inválida para comportamento",
                )

            interaction_type_db = interaction_enum_map[action_type]

            behavior = (
                db.query(TrackBehavior)
                .filter_by(
                    user_id=user.id,
                    track_id=track_id,
                    interaction_type=interaction_type_db,
                )
                .first()
            )

            if behavior:
                behavior.count += 1
            else:
                new_behavior = TrackBehavior(
                    user_id=user.id,
                    track_id=track_id,
                    interaction_type=interaction_type_db,
                    count=1,
                )
                db.add(new_behavior)

            message = f"Comportamento '{action_type}' incrementado com sucesso."

        db.commit()

        return InteractionResponse(message=message, track_id=track_id, type=action_type)
