from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.api import deps
from app.models.user import User
from app.services.player import PlayerService
from app.schemas.player import (
    PlayRequest,
    VolumeRequest,
    ShuffleRequest,
    RepeatRequest,
    TransferRequest,
)

router = APIRouter()

@router.put("/play")
async def play(
    request: PlayRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Inicia ou retoma a reprodução.
    
    Permite passar uma música individual, uma lista de músicas ou um contexto (álbum/playlist).
    """
    return await PlayerService.play(
        db,
        current_user,
        uri=request.uri,
        uris=request.uris,
        context_uri=request.context_uri,
        offset=request.offset,
        device_id=request.device_id,
    )

@router.post("/pause")
async def pause(
    device_id: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Pausa a reprodução no dispositivo especificado ou no ativo.
    """
    return await PlayerService.pause(db, current_user, device_id)

@router.post("/resume")
async def resume(
    device_id: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retoma a reprodução no dispositivo especificado ou no ativo.
    """
    return await PlayerService.resume(db, current_user, device_id)

@router.post("/next")
async def next_track(
    device_id: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Pula para a próxima faixa.
    """
    return await PlayerService.next(db, current_user, device_id)

@router.post("/previous")
async def previous_track(
    device_id: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Volta para a faixa anterior.
    """
    return await PlayerService.previous(db, current_user, device_id)

@router.put("/volume")
async def set_volume(
    request: VolumeRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Define o nível de volume (0-100).
    """
    return await PlayerService.set_volume(
        db, current_user, request.volume_percent, request.device_id
    )

@router.put("/shuffle")
async def set_shuffle(
    request: ShuffleRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Ativa ou desativa o modo shuffle.
    """
    return await PlayerService.set_shuffle(
        db, current_user, request.state, request.device_id
    )

@router.put("/repeat")
async def set_repeat_mode(
    request: RepeatRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Define o modo de repetição (off, track, context).
    """
    return await PlayerService.set_repeat_mode(
        db, current_user, request.state, request.device_id
    )

@router.post("/transfer")
async def transfer_playback(
    request: TransferRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Transfere a reprodução para um novo dispositivo.
    """
    return await PlayerService.transfer_playback(
        db, current_user, request.device_id, request.play
    )

@router.get("/queue")
async def get_queue(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtém a fila de reprodução.
    """
    return await PlayerService.get_queue(db, current_user)

@router.get("/now-playing")
async def get_now_playing(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtém informações da faixa atual.
    """
    return await PlayerService.get_now_playing(db, current_user)

@router.get("/devices")
async def get_devices(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Lista dispositivos disponíveis.
    """
    return await PlayerService.get_devices(db, current_user)
