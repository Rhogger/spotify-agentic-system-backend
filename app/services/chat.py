import logging
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.agent import root_agent
from app.schemas.chat import ChatResponse
from app.models.user import User

logger = logging.getLogger(__name__)

APP_NAME = "spotify-agent"
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent, app_name=APP_NAME, session_service=session_service
)


class ChatService:
    @staticmethod
    async def process_message(message: str, user: User) -> ChatResponse:
        """
        Processa a mensagem do usuário usando o Google ADK Runner.
        Gerencia sessão baseada no ID do usuário logado.
        
        Args:
            message: A mensagem do usuário
            user: O objeto User autenticado (passado explicitamente para garantir propagação)
        """
        user_id = str(user.id)
        session_id = f"session_{user_id}"

        initial_state = {
            "user:id": user.id,
            "user:spotify_id": user.spotify_id,
            "user:spotify_access_token": user.spotify_access_token,
            "user:spotify_refresh_token": user.spotify_refresh_token,
            "user:email": user.email,
            "user:display_name": user.display_name,
        }

        existing_session = await session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        
        if not existing_session:
            await session_service.create_session(
                app_name=APP_NAME, user_id=user_id, session_id=session_id, state=initial_state
            )
            logger.info(f"Sessão criada: {session_id} para usuário {user_id} ({user.display_name})")
        else:
            old_token = existing_session.state.get("user:spotify_access_token")
            new_token = user.spotify_access_token
            
            if old_token != new_token:
                await session_service.delete_session(
                    app_name=APP_NAME, user_id=user_id, session_id=session_id
                )
                await session_service.create_session(
                    app_name=APP_NAME, user_id=user_id, session_id=session_id, state=initial_state
                )
                logger.info(f"Sessão recriada (token renovado): {session_id}")
            else:
                existing_session.state.update(initial_state)
                logger.info(f"Sessão existente reutilizada: {session_id}")

        content = types.Content(role="user", parts=[types.Part(text=message)])

        final_response_text = ""

        try:
            async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=content
            ):
                logger.debug(f"Event ID: {event.id}, Author: {event.author}, Is Final: {event.is_final_response()}")
                
                if event.is_final_response():
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                final_response_text += part.text
                                logger.info(f"Resposta capturada de '{event.author}': {part.text[:100]}...")

            if not final_response_text:
                logger.warning("Nenhuma resposta final capturada do agente.")
                final_response_text = (
                    "Desculpe, não consegui processar sua solicitação. Tente novamente."
                )

            return ChatResponse(response=final_response_text)

        except Exception as e:
            logger.error(f"Erro na execução do Runner ADK: {e}", exc_info=True)
            raise e

    @staticmethod
    async def reset_session(user: User) -> None:
        """
        Reinicia a sessão do usuário, deletando a existente e criando uma nova.
        
        Args:
            user: O objeto User autenticado
        """
        user_id = str(user.id)
        session_id = f"session_{user_id}"

        existing_session = await session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        
        if existing_session:
            await session_service.delete_session(
                app_name=APP_NAME, user_id=user_id, session_id=session_id
            )
            logger.info(f"Sessão deletada: {session_id}")

        initial_state = {
            "user:id": user.id,
            "user:spotify_id": user.spotify_id,
            "user:spotify_access_token": user.spotify_access_token,
            "user:spotify_refresh_token": user.spotify_refresh_token,
            "user:email": user.email,
            "user:display_name": user.display_name,
        }

        await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id, state=initial_state
        )
        logger.info(f"Nova sessão criada: {session_id} para usuário {user_id} ({user.display_name})")
