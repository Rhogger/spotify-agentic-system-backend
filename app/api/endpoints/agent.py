from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Envia uma mensagem para o Agente Orquestrador.
    O usuário autenticado é passado explicitamente ao ChatService.
    """
    try:
        return await ChatService.process_message(request.message, current_user)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar mensagem com Agente: {str(e)}"
        )


@router.post("/session/reset")
async def reset_session(
    current_user: User = Depends(get_current_user),
):
    """
    Reinicia a sessão do agente para o usuário atual.
    Útil quando o histórico está poluído ou o usuário quer começar uma nova conversa.
    """
    try:
        await ChatService.reset_session(current_user)
        return {"message": "Sessão reiniciada com sucesso"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao reiniciar sessão: {str(e)}"
        )
