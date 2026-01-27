import httpx
from urllib.parse import urlencode
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.config import settings
from app.models.user import User


class AuthService:
    @staticmethod
    def get_login_url() -> str:
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

        return f"https://accounts.spotify.com/authorize?{urlencode(params)}"

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
            raise HTTPException(
                status_code=400, detail=f"Erro no Spotify Auth: {resp.text}"
            )

        return resp.json()

    @staticmethod
    async def get_spotify_profile(access_token: str) -> dict:
        """Busca o perfil do usuário no Spotify."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.spotify.com/v1/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Erro ao buscar perfil do usuário no Spotify"
            )

        return resp.json()

    @staticmethod
    def get_or_create_user(db: Session, spotify_profile: dict, tokens: dict) -> User:
        """Cria ou atualiza o usuário no banco de dados local."""
        spotify_id = spotify_profile.get("id")
        email = spotify_profile.get("email")

        user = db.query(User).filter(User.spotify_id == spotify_id).first()

        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token")

        print(f"\n\n\nAccess Token: {access_token} \n\n\n")

        if not user:
            user = User(
                spotify_id=spotify_id,
                email=email,
                display_name=spotify_profile.get("display_name"),
                spotify_access_token=access_token,
                spotify_refresh_token=refresh_token,
            )
            db.add(user)
        else:
            user.spotify_access_token = access_token
            if refresh_token:
                user.spotify_refresh_token = refresh_token
            user.display_name = spotify_profile.get("display_name")
            user.email = email

        db.commit()
        db.refresh(user)
        return user
