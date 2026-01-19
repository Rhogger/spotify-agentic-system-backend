```mermaid
flowchart LR
 subgraph App["🖥️ Aplicação"]
        Frontend["Frontend"]
        Backend["Backend"]
  end
 subgraph Brain["🧠 Orquestração"]
    direction TB
        Orchestrator{{"🤖 Orquestrador"}}
        Librarian["📚 Coletador de dados"]
        DJ["🎧 DJ"]
        Curator["🎻 Curador"]
        Vibe["🧪 Recomendador"]
        Summarizer["📝 Formatador de Texto"]
  end
 subgraph T_Search["🔍 Consultas"]
        t1("search_db_tracks")
        t2("get_track_features")
  end
 subgraph T_Player["⏯️ Player"]
        t3("play_music")
        t4("control_playback")
        t5("get_now_playing")
  end
 subgraph T_Manage["📂 Músicas e Playlists"]
        t6("create_playlist")
        t7("delete_playlist")
        t8("add_track_to_pl")
        t9("remove_track_from_pl")
        t10("toggle_like")
  end
 subgraph T_ML["🔮 Recomendação"]
        t11("recommend_by_features")
        t12("recommend_by_seed_track")
  end
 subgraph T_Format["📄 Formatação"]
        t13("clean_text_format")
  end
 subgraph Toolbox["🛠️ Ferramentas"]
    direction TB
        T_Search
        T_Player
        T_Manage
        T_ML
        T_Format
  end
 subgraph External["💾 Dados & Serviços"]
    direction TB
        DB[("Postgres Local")]
        MCP["MCP Server"]
        ML(("Modelo .joblib"))
        Spotify(("Spotify API"))
  end
    User(["👤 Usuário"]) <--> Frontend
    Frontend <--> Backend
    Backend --> Orchestrator
    Orchestrator --> Librarian & DJ & Curator & Vibe
    Librarian --> t1 & t2 & Summarizer
    DJ --> t3 & t4 & t5 & Summarizer
    Curator --> Summarizer & t6 & t7 & t8 & t9 & t10
    Vibe --> Summarizer & t11 & t12
    Summarizer -- Resposta Final --> Backend
    Summarizer --> t13
    T_Search --> DB
    t12 -. Busca Features .-> DB
    T_ML --> ML
    T_Manage --> DB
    T_Manage -. Se Toggle ON .-> MCP
    T_Player --> MCP
    MCP <--> Spotify

     Frontend:::app
     Backend:::app
     Orchestrator:::orchestrator
     Librarian:::agent
     DJ:::agent
     Curator:::agent
     Vibe:::agent
     Summarizer:::finalizer
     t1:::tool
     t2:::tool
     t3:::tool
     t4:::tool
     t5:::tool
     t6:::tool
     t7:::tool
     t8:::tool
     t9:::tool
     t10:::tool
     t11:::tool
     t12:::tool
     t13:::tool
     DB:::resource
     MCP:::resource
     ML:::resource
     Spotify:::resource
     User:::user
    classDef app fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef orchestrator fill:#e1bee7,stroke:#4a148c,stroke-width:3px
    classDef agent fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef tool fill:#fff3e0,stroke:#e65100,stroke-width:1px,stroke-dasharray:5,5
    classDef resource fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef finalizer fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    classDef user fill:transparent, stroke:#333, stroke-width:2px
    style Frontend fill:transparent
    style Backend fill:transparent
    style Orchestrator fill:transparent
    style Librarian fill:transparent
    style DJ fill:transparent
    style Curator fill:transparent
    style Vibe fill:transparent
    style Summarizer fill:transparent
    style t1 fill:transparent
    style t2 fill:transparent
    style t3 fill:transparent
    style t4 fill:transparent
    style t5 fill:transparent
    style t6 fill:transparent
    style t7 fill:transparent
    style t8 fill:transparent
    style t9 fill:transparent
    style t10 fill:transparent
    style t11 fill:transparent
    style t12 fill:transparent
    style t13 fill:transparent
    style T_Search stroke:#424242,fill:transparent
    style T_Player fill:transparent,stroke:#424242
    style T_Manage stroke:#424242,fill:transparent
    style T_ML stroke:#424242,fill:transparent
    style T_Format stroke:#424242,fill:transparent
    style DB fill:transparent
    style MCP fill:transparent
    style ML fill:transparent
    style Spotify fill:transparent
    style User fill:transparent
    style App stroke:#424242,fill:transparent
    style Brain stroke:#424242,fill:transparent
    style Toolbox stroke:#424242,fill:transparent
    style External stroke:#424242,fill:transparent
