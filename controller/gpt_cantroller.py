from typing import List, Dict, Any

from fastapi import HTTPException, APIRouter, Body
from service import gpt_service
from openai import OpenAI
import os

router = APIRouter(prefix="/gpt", tags=["gpt"])
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@router.get("/content/{user_id}")
async def get_assistant_context(user_id: int):
    try:
        content_string = await gpt_service.get_assistant_context(user_id)
        return {"context": content_string}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

