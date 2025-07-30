# ------------------------------------- External Imports -------------------------------------

# FastAPI tools
from fastapi import APIRouter, HTTPException

# Pydantic model
from pydantic import BaseModel

# ------------------------------------- Internal Imports -------------------------------------

# Ollama call logic
from .llm_client import query_llm


# ------------------------------------- Router Setup -------------------------------------

router = APIRouter(prefix="/llm", tags=["LLM"])


# ------------------------------------- Input Schema -------------------------------------

class LLMRequest(BaseModel):
    prompt: str


# ------------------------------------- Endpoint: LLM Chat -------------------------------------

@router.post("/chat")
async def llm_chat(request: LLMRequest):
    """
    Endpoint to interact with the local LLM.
    """
    response = await query_llm(prompt=request.prompt)

    if response is None:
        raise HTTPException(status_code=500, detail="LLM failed to respond")

    return {"response": response}
