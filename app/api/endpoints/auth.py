from app.services.playlists import PlaylistsService
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth import AuthService
from app.core.security import create_access_token
from app.core.config import settings

router = APIRouter()


@router.get("/login")
async def login_spotify():
    """
    1. Redireciona o usuário para a tela de consentimento do Spotify.
    """
    url = await AuthService.get_login_url()
    return RedirectResponse(url)


@router.get("/callback")
async def spotify_callback(code: str, db: Session = Depends(get_db)):
    """
    2. Recebe o 'code' do Spotify, troca por tokens e cria a sessão.
    """

    tokens = await AuthService.exchange_code_for_token(code)

    if "access_token" not in tokens:
        raise HTTPException(
            status_code=400, detail="Token não encontrado na resposta do Spotify"
        )

    spotify_profile = await AuthService.get_spotify_profile(tokens["access_token"])
    if not spotify_profile:
        raise HTTPException(
            status_code=400,
            detail="Erro ao buscar perfil do usuário no Spotify (token inválido?)",
        )

    user = AuthService.get_or_create_user(db, spotify_profile, tokens)

    await PlaylistsService.create_playlist(db, "Músicas curtidas", user.id)

    internal_access_token = create_access_token(
        subject=user.id, expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    internal_refresh_token = create_access_token(
        subject=user.id, expires_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    frontend_url = f"http://localhost:3001/auth/callback?token={internal_access_token}&refresh={internal_refresh_token}"

    return RedirectResponse(frontend_url)
