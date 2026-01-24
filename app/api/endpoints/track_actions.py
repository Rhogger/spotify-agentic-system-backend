from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.track import Track
from app.models.track_preference import TrackPreference
from app.models.track_behavior import TrackBehavior, InteractionType
from app.schemas.track_interaction import InteractionTypeEnum, InteractionResponse

router = APIRouter()

@router.post("/{track_id}/action", response_model=InteractionResponse)
def register_track_action(
    track_id: int,
    type: InteractionTypeEnum,
    user_id: int = Query(..., description="ID do utilizador (temporário sem auth)"),
    db: Session = Depends(get_db)
):
    # 1. Validação: O track_id existe?
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Música não encontrada no catálogo")

    # 2. Fluxo de Preferência (LIKE / DISLIKE)
    if type in [InteractionTypeEnum.LIKE, InteractionTypeEnum.DISLIKE]:
        is_liked = (type == InteractionTypeEnum.LIKE)
        
        # Tenta encontrar registo existente (Upsert)
        pref = db.query(TrackPreference).filter_by(user_id=user_id, track_id=track_id).first()
        
        if pref:
            pref.liked = is_liked
        else:
            new_pref = TrackPreference(user_id=user_id, track_id=track_id, liked=is_liked)
            db.add(new_pref)
            
        message = f"Preferência '{type}' registada com sucesso."

    # 3. Fluxo de Comportamento (SKIP / BACK / VIEW)
    else:
        # Mapear InteractionTypeEnum para InteractionType enum
        interaction_enum_map = {
            InteractionTypeEnum.SKIP: InteractionType.SKIP,
            InteractionTypeEnum.BACK: InteractionType.BACK,
            InteractionTypeEnum.VIEW: InteractionType.VIEW,
        }
        interaction_type_enum = interaction_enum_map[type]
        
        # Tenta encontrar registo existente para incrementar (Upsert com Incremento)
        behavior = db.query(TrackBehavior).filter_by(
            user_id=user_id, 
            track_id=track_id, 
            interaction_type=interaction_type_enum
        ).first()
        
        if behavior:
            behavior.count += 1
        else:
            new_behavior = TrackBehavior(
                user_id=user_id, 
                track_id=track_id, 
                interaction_type=interaction_type_enum, 
                count=1
            )
            db.add(new_behavior)
            
        message = f"Comportamento '{type}' incrementado com sucesso."

    db.commit()
    return {
        "message": message,
        "track_id": track_id,
        "type": type
    }