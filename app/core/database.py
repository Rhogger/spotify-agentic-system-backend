from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency para ser usada nas rotas FastAPI.
    Cria uma sessão nova para cada requisição e fecha ao terminar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
