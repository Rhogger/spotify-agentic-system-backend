import httpx
from urllib.parse import urlencode
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.config import settings
from app.models.user import User
from app.core.logger import logger


class AuthService:
    @staticmethod
    async def get_login_url() -> str:
        """Gera a URL de autorização do Spotify com os escopos necessários."""
        scopes = [
            "user-read-private",
            "user-read-email",
            "user-read-playback-state",
            "user-modify-playback-state",
            "user-read-currently-playing",
            "playlist-read-private",
            "playlist-modify-private",
            "playlist-modify-public",
            "user-library-read",
            "user-library-modify",
            "user-read-recently-played",
        ]

        params = {
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "scope": " ".join(scopes),
            "show_dialog": "true",
        }

        url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
        logger.info(f"Gerando URL de login: {url}")
        return url

    @staticmethod
    async def exchange_code_for_token(code: str) -> dict:
        """Troca o authorization code por tokens de acesso."""
        token_url = "https://accounts.spotify.com/api/token"

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
                    "client_id": settings.SPOTIFY_CLIENT_ID,
                    "client_secret": settings.SPOTIFY_CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if resp.status_code != 200:
            logger.error(
                f"Erro no Spotify Auth (Exchange): {resp.status_code} - {resp.text}"
            )
            raise HTTPException(
                status_code=400, detail=f"Erro no Spotify Auth: {resp.text}"
            )

        data = resp.json()
        logger.success("Troca de Token com Sucesso", data=data)
        return data

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> dict:
        """Renova o access_token usando o refresh_token."""
        token_url = "https://accounts.spotify.com/api/token"

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": settings.SPOTIFY_CLIENT_ID,
                    "client_secret": settings.SPOTIFY_CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if resp.status_code != 200:
            logger.error(
                f"Erro ao renovar token Spotify: {resp.status_code} - {resp.text}"
            )
            raise HTTPException(
                status_code=400, detail=f"Erro ao renovar token: {resp.text}"
            )

        data = resp.json()
        logger.success("Renovação de Token com Sucesso", data=data)
        return data

    @staticmethod
    async def get_spotify_profile(access_token: str) -> dict:
        """Busca o perfil do usuário no Spotify. Apenas valida o token."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.spotify.com/v1/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if resp.status_code != 200:
            logger.error(
                f"Erro ao buscar perfil do usuário no Spotify: {resp.status_code} - {resp.text}"
            )
            return None

        data = resp.json()
        logger.success("Perfil Spotify Recuperado", data=data)
        return data

    @staticmethod
    async def get_spotify_profile_with_refresh(db: Session, user: User) -> dict:
        """Busca o perfil, se der 401 tenta refresh e salva no DB."""
        profile = await AuthService.get_spotify_profile(user.spotify_access_token)

        if profile:
            return profile

        if not user.spotify_refresh_token:
            logger.error("Token expirado e sem refresh token")
            raise HTTPException(
                status_code=401, detail="Token expirado e sem refresh token"
            )

        new_tokens = await AuthService.refresh_access_token(user.spotify_refresh_token)

        user.spotify_access_token = new_tokens["access_token"]
        if "refresh_token" in new_tokens:
            user.spotify_refresh_token = new_tokens["refresh_token"]

        db.add(user)
        db.commit()
        db.refresh(user)

        profile = await AuthService.get_spotify_profile(user.spotify_access_token)
        if not profile:
            logger.error("Erro ao buscar perfil mesmo após refresh")
            raise HTTPException(
                status_code=400, detail="Erro ao buscar perfil mesmo após refresh"
            )

        return profile

    @staticmethod
    def get_or_create_user(db: Session, spotify_profile: dict, tokens: dict) -> User:
        """Cria ou atualiza o usuário no banco de dados local."""
        spotify_id = spotify_profile.get("id")
        email = spotify_profile.get("email")

        user = db.query(User).filter(User.spotify_id == spotify_id).first()

        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token")

        msg = (
            f"Token de Acesso do Usuário: {access_token[:10]}..."
            if access_token
            else "Sem Token de Acesso"
        )
        logger.debug(msg)

        if not user:
            logger.info(f"Criando novo usuário: {email}")
            user = User(
                spotify_id=spotify_id,
                email=email,
                display_name=spotify_profile.get("display_name"),
                spotify_access_token=access_token,
                spotify_refresh_token=refresh_token,
            )
            db.add(user)
        else:
            logger.info(f"Atualizando usuário existente: {email}")
            user.spotify_access_token = access_token
            if refresh_token:
                user.spotify_refresh_token = refresh_token
            user.display_name = spotify_profile.get("display_name")
            user.email = email

        db.commit()
        db.refresh(user)
        return user
