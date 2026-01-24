"""add_trgm_and_indices

Revision ID: 83724e1ed488
Revises: 95202d466851
Create Date: 2026-01-24 13:30:56.961371

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83724e1ed488'
down_revision: Union[str, Sequence[str], None] = '95202d466851'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Habilita a extensão para busca por similaridade
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    
    # Cria um índice GIN na concatenação de nome e artistas
    # Nota: Usamos a sintaxe PostgreSQL específica para o índice
    op.execute("""
        CREATE INDEX idx_tracks_name_artists_trgm ON tracks 
        USING gin ((name || ' ' || artists) gin_trgm_ops);
    """)

def downgrade():
    op.execute("DROP INDEX idx_tracks_name_artists_trgm;")
    op.execute("DROP EXTENSION IF NOT EXISTS pg_trgm;")