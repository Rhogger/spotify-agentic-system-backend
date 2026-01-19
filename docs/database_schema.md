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
        boolean 1920s
        boolean 1930s
        boolean 1940s
        boolean 1950s
        boolean 1960s
        boolean 1970s
        boolean 1980s
        boolean 1990s
        boolean 2000s
        boolean 2010s
        boolean 2020s
    }

    PLAYLIST ||--o{ PLAYLIST_ITEM : contains
    PLAYLIST {
        string id PK
        string owner_id FK
        string name 
    }

    PLAYLIST_ITEM {
        int id PK
        string playlist_id FK
        string track_id FK
        datetime added_at
    }

    INTERACTION {
        int id PK
        string user_id FK
        string track_id FK
        datetime timestamp
    }