from fastapi import APIRouter, HTTPException
from service import gpt_service
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter(prefix="/gpt", tags=["gpt"])

@router.get("/content/{user_id}")
async def get_assistant_context(user_id: int):
    try:
        content_string = await gpt_service.get_assistant_context(user_id)
        return {"context": content_string}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
