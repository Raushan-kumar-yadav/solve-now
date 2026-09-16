from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from services.ai.factory import get_ai_provider

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    problem_context: Optional[str] = None
    action_type: str = "chat" # chat, hint, explain, debug, review, optimize

class ChatResponse(BaseModel):
    response: str
    provider: str

@router.post("/chat", response_model=ChatResponse)
def ai_chat(req: ChatRequest):
    try:
        provider = get_ai_provider()
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Provider Initialization Error: {str(err)}"
        )
    
    system_prompt = "You are SolveNow's expert AI assistant."
    
    if req.problem_context:
        system_prompt += f"\n\nContext:\n{req.problem_context}"
        
    if req.action_type == "hint":
        system_prompt += "\n\nProvide a gentle hint to point the user in the right direction without revealing the complete solution."
    elif req.action_type == "explain":
        system_prompt += "\n\nExplain the concepts involved in this problem clearly."
    elif req.action_type == "debug":
        system_prompt += "\n\nHelp the user debug their code or approach."
    elif req.action_type == "review":
        system_prompt += "\n\nReview the user's proposed solution or code."
    elif req.action_type == "optimize":
        system_prompt += "\n\nSuggest optimizations for time and space complexity."
        
    try:
        response_text = provider.generate_chat_response(prompt=req.message, system_prompt=system_prompt)
        return {"response": response_text, "provider": type(provider).__name__}
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI Service Error: {str(e)}")
