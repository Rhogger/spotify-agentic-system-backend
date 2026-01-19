# Database Schema - Spotify Agentic System

Este documento detalha a modelagem de dados do backend, servindo como guia para a implementação dos modelos SQLAlchemy e para a compreensão das relações entre usuários, músicas e agentes.

## Diagrama Entidade-Relacionamento (ERD)

```mermaid
erDiagram
    USER ||--o{ PLAYLIST : owner
    USER ||--o{ INTERACTION : performs
    USER {
        string id PK
        string display_name
        string email
        datetime created_at "Auditoria"
        boolean system_deleted "Soft Delete"
    }

    TRACK ||--o{ PLAYLIST_ITEM : part_of
    TRACK ||--o{ INTERACTION : receives
    TRACK {
        string id PK "Spotify Track ID"
        string name
        string artists
        int duration_ms
        float acousticness
        float danceability
        float energy
        float instrumentalness
        float speechiness
        float valence
        boolean explicit
        boolean is_popular
        boolean d_1920s
        boolean d_1930s
        boolean d_1940s
        boolean d_1950s
        boolean d_1960s
        boolean d_1970s
        boolean d_1980s
        boolean d_1990s
        boolean d_2000s
        boolean d_2010s
        boolean d_2020s
        datetime created_at "Auditoria"
        boolean system_deleted "Soft Delete"
    }

    PLAYLIST ||--o{ PLAYLIST_ITEM : contains
    PLAYLIST {
        string id PK
        string owner_id FK
        string name 
        datetime created_at "Auditoria"
        boolean system_deleted "Soft Delete"
    }

    PLAYLIST_ITEM {
        int id PK
        string playlist_id FK
        string track_id FK
        datetime created_at "Auditoria"
        boolean system_deleted "Soft Delete"
    }

    INTERACTION {
        int id PK
        string user_id FK
        string track_id FK
        datetime created_at "Auditoria"
        boolean system_deleted "Soft Delete"
    }