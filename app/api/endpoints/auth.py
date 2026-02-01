from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth import AuthService
from app.core.security import create_access_token
from app.core.config import settings
from app.core.logger import logger

router = APIRouter()


@router.get(
    "/login",
    summary="Inicia login com Spotify",
    description="Redireciona o usuário para a página de autorização do Spotify (OAuth2).",
)
async def login_spotify():
    """
    1. Redireciona o usuário para a tela de consentimento do Spotify.
    """
    logger.info("Iniciando fluxo de login via Spotify")
    url = await AuthService.get_login_url()
    return RedirectResponse(url)


@router.get(
    "/callback",
    summary="Callback de Autenticação",
    description="Recebe o código de autorização do Spotify, troca por tokens de acesso/refresh e cria a sessão do usuário no sistema.",
)
async def spotify_callback(code: str, db: Session = Depends(get_db)):
    """
    2. Recebe o 'code' do Spotify, troca por tokens e cria a sessão.
    """

    logger.info("Código de callback recebido, iniciando troca de tokens")
    tokens = await AuthService.exchange_code_for_token(code)

    if "access_token" not in tokens:
        logger.error("Token de acesso não encontrado na resposta do Spotify")
        raise HTTPException(
            status_code=400, detail="Token não encontrado na resposta do Spotify"
        )

    spotify_profile = await AuthService.get_spotify_profile(tokens["access_token"])
    if not spotify_profile:
        logger.error("Erro ao buscar perfil do usuário no Spotify (token inválido?)")
        raise HTTPException(
            status_code=400,
            detail="Erro ao buscar perfil do usuário no Spotify (token inválido?)",
        )

    user = AuthService.get_or_create_user(db, spotify_profile, tokens)

    internal_access_token = create_access_token(
        subject=user.id, expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    internal_refresh_token = create_access_token(
        subject=user.id, expires_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    frontend_url = f"http://localhost:3001/auth/callback?token={internal_access_token}&refresh={internal_refresh_token}"

    logger.success(
        "Login finalizado com sucesso. Redirecionando para frontend.",
        data={"user": user.email},
    )
    return RedirectResponse(frontend_url)
