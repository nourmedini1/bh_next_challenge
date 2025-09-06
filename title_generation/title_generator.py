from fastapi import FastAPI, HTTPException,Response
from parlant.client import ParlantClient
from langchain_mistralai import ChatMistralAI
import uvicorn
from pydantic import BaseModel
from typing import List
import os


class TitleGenerationRequest(BaseModel):
    messages: List[str]
    session_id: str


llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0.7,
    api_key=os.environ.get("TITLE_GENERATOR_API_KEY")
)

app = FastAPI()
client = ParlantClient(base_url="http://localhost:8800")



@app.post("/generate-title/")
async def generate_title(request : TitleGenerationRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages are required")
    prompt = f"Generate a concise and catchy title for the following conversation: {' '.join(request.messages)}"
    response = await llm.ainvoke(prompt)
    title = response.content[0]
    client.sessions.update(session_id=request.session_id, title=title)
    return Response(status_code=204)


uvicorn.run(app, host="0.0.0.0", port=6003)
