from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.users import UserService
from app.core.logger import logger

security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Valida o Token JWT e retorna o objeto User do banco.
    Se falhar, lança erro 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token JWT inválido: user_id não encontrado no payload")
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"Erro ao decodificar token JWT: {e}")
        raise credentials_exception

    user = UserService.get(db, int(user_id))
    if user is None:
        logger.warning(f"Usuário ID {user_id} do token não encontrado no banco")
        raise credentials_exception

    return user
