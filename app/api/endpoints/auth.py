from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
from urllib.parse import urlencode

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.core.security import create_access_token

router = APIRouter()


@router.get("/login")
def login_spotify():
    """
    1. Redireciona o usuário para a tela de consentimento do Spotify.
    """
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
    return RedirectResponse(url)


@router.get("/callback")
async def spotify_callback(code: str, db: Session = Depends(get_db)):
    """
    2. Recebe o 'code' do Spotify, troca por tokens e cria a sessão.
    """

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
        raise HTTPException(status_code=400, detail=f"Erro no Spotify: {resp.text}")

    token_data = resp.json()
    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")

    print("access_token: " + access_token)

    async with httpx.AsyncClient() as client:
        me_resp = await client.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if me_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Erro ao pegar perfil do usuário")

    me_data = me_resp.json()

    user = db.query(User).filter(User.spotify_id == me_data["id"]).first()

    if not user:
        user = User(
            spotify_id=me_data["id"],
            email=me_data["email"],
            display_name=me_data.get("display_name"),
            spotify_access_token=access_token,
            spotify_refresh_token=refresh_token,
        )
        db.add(user)
    else:
        user.spotify_access_token = access_token
        if refresh_token:
            user.spotify_refresh_token = refresh_token
        user.display_name = me_data.get("display_name")

    db.commit()
    db.refresh(user)

    internal_token = create_access_token(subject=user.id)

    frontend_url = f"http://localhost:3000/auth/callback?token={internal_token}"

    return RedirectResponse(frontend_url)
