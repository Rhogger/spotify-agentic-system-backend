from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from app.core.config import settings


def create_access_token(
    subject: Union[str, Any],
    expires_minutes: int,
    expires_delta: timedelta = None,
) -> str:
    """
    Gera um JWT assinado com a nossa SECRET_KEY.
    O 'subject' é o ID do usuário no banco.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    to_encode = {"exp": expire, "sub": str(subject)}

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
