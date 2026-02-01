from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService

from app.core.logger import logger

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Envia mensagem ao Agente",
    description="Envia uma mensagem de texto para o Agente Orquestrador. O agente processa a intenção do usuário e interage com os serviços do Spotify para realizar ações.",
)
async def chat_with_agent(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Envia uma mensagem para o Agente Orquestrador.
    O usuário autenticado é passado explicitamente ao ChatService.
    """
    try:
        logger.info(f"Requisição de chat recebida. Mensagem: {request.message[:50]}...")
        return await ChatService.process_message(request.message, current_user)

    except Exception as e:
        logger.error(f"Erro no endpoint de chat: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar mensagem com Agente: {str(e)}"
        )


@router.post(
    "/session/reset",
    summary="Reinicia a sessão do Agente",
    description="Limpa o histórico de conversas e o estado da sessão do agente para o usuário atual. Útil para iniciar um novo contexto.",
)
async def reset_session(
    current_user: User = Depends(get_current_user),
):
    """
    Reinicia a sessão do agente para o usuário atual.
    Útil quando o histórico está poluído ou o usuário quer começar uma nova conversa.
    """
    try:
        logger.info(f"Solicitação de reset de sessão para usuário {current_user.id}")
        await ChatService.reset_session(current_user)
        return {"message": "Sessão reiniciada com sucesso"}

    except Exception as e:
        logger.error(f"Erro ao reiniciar sessão: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao reiniciar sessão: {str(e)}"
        )
