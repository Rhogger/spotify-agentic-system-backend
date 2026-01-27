# Contexto do Projeto: Spotify Agentic System (Backend & Agents)

Este documento descreve a visão conceitual e arquitetural do backend do **Spotify Agentic System**. O projeto integra uma API robusta, um modelo de recomendação via IA, ferramentas de controle do Spotify (MCP) e Agentes inteligentes para entregar uma experiência musical completa.

## 1. Visão do Produto

O sistema atua como uma camada inteligente sobre a experiência musical do usuário, permitindo gerenciamento avançado de biblioteca, recomendações personalizadas e controle de reprodução através de uma interface conversacional e de uma API estruturada.

## 2. Componentes e Capacidades

O sistema é dividido em quatro camadas principais de responsabilidade: **API de Backend**, **Integração MCP**, **Modelo de IA** e **Agentes**.

### A. API de Backend (O Gerenciador de Dados)

A API REST é responsável pela persistência, autenticação e gestão dos dados locais do sistema.

- **Autenticação e Usuários:**
  - Login via provedor externo.
  - Criação automática de usuário no primeiro acesso.
- **Gestão de Playlists (Local):**
  - Criar e deletar playlists no banco de dados do sistema.
  - Visualizar uma ou múltiplas playlists.
- **Catálogo Musical:**
  - Visualizar lista de músicas (com paginação).
  - Visualizar detalhes técnicos e metadados de uma música específica.
  - Buscar músicas dentro das playlists existentes.
- **Rastreamento de Comportamento (Analytics):**
  - Registrar ações do usuário para alimentar o modelo de recomendação: `view` (visualizou), `like`, `dislike`, `skip` (pulou) e `back` (voltou).

### B. Integração MCP (O Braço no Spotify)

O Model Context Protocol (MCP) é a ponte exclusiva para interagir com a conta oficial do Spotify do usuário. Todas as mudanças reais na conta ou no player passam por aqui.

- **Controle de Biblioteca:**
  - Criar playlists reais na conta do Spotify.
  - Adicionar músicas a playlists do Spotify.
- **Controle de Playback:**
  - Comandar `Play` e `Pause` no dispositivo ativo.

### C. Modelo de IA - KNN (O Cérebro de Recomendação)

O sistema utiliza algoritmos de Machine Learning (K-Nearest Neighbors) para inteligência musical.

- **Geração de Recomendações:**
  - Sugerir novas músicas com base no histórico e gosto do usuário.
- **Recomendação Baseada em Features:**
  - Funcionalidade específica que localiza uma música de referência, extrai suas "features" de áudio (danceability, energy, acousticness, etc.) e encontra músicas matematicamente similares no banco de dados.

### D. Agentes (A Força de Trabalho)

Os Agentes são as entidades autônomas que orquestram o uso de todas as camadas acima. Eles "conversam" com o usuário e decidem qual ferramenta usar.

- **Recursos do Agente:**
  - **Gestão de Conteúdo:** Criar e deletar playlists (acionando a API ou MCP conforme necessário).
  - **Edição de Playlists:** Adicionar e remover músicas de playlists.
  - **Exploração:** Visualizar listas de músicas paginadas e acessar dados detalhados de faixas.
  - **Busca:** Pesquisar músicas diretamente no banco de dados local.
  - **Controle:** Utilizar as ferramentas do MCP para controlar o Spotify real.
  - **Curadoria:** Acionar o modelo de IA para gerar recomendações personalizadas e apresentá-las ao usuário.

## 3. Fluxo de Interação Exemplo

1.  **Usuário:** "Crie uma playlist com músicas parecidas com 'Bohemian Rhapsody'."
2.  **Agente:**
    - Usa a **Busca (API)** para achar 'Bohemian Rhapsody' e pegar seu ID.
    - Aciona a **Função de Features (IA)** para encontrar músicas similares.
    - Chama o **MCP** para criar a playlist vazia no Spotify.
    - Chama o **MCP** novamente para adicionar as músicas recomendadas.
    - Responde ao usuário: "Playlist criada com sucesso baseada na complexidade de Queen."

## 4. Diferenciais Técnicos

- **Rastreamento de Interações:** Diferente de players comuns, o sistema aprende com `skips` e `back` para refinar futuras recomendações.
- **Hibridismo:** Combina dados locais (rápidos e customizáveis) com a API oficial do Spotify (para execução real).
