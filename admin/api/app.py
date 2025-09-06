import traceback
from typing import List
from fastapi import FastAPI,HTTPException,Response
from fastapi.middleware.cors import CORSMiddleware
from parlant.client import ParlantClient
from parlant.sdk import Agent,Tag,Term,Guideline,Journey
import uvicorn
from models import * 
from utils import *

app = FastAPI(title="Admin API")

client = ParlantClient(base_url="http://localhost:8800")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -------------------------------- AGENTS ---------------------------------------------
@app.get("/agents")
async def get_agents():
    try:
        agents : List[Agent] =  client.agents.list()
        if not agents:
            return Response(status_code=204)
        agents_json = [map_agent_to_agent_response(agent) for agent in agents]
        return agents_json
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    try:
        agent: Agent =  client.agents.retrieve(agent_id=agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return map_agent_to_agent_response(agent)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/agents/{agent_id}")
async def update_agent(agent_id: str, agent_data: UpdateAgentRequest):
    try:
        agent: Agent =  client.agents.retrieve(agent_id=agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        updated_agent =  client.agents.update(agent_id=agent_id, **agent_data.model_dump())
        return Response(status_code=200, content=map_agent_to_agent_response(updated_agent), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------ TAGS ---------------------------------

@app.get("/tags")
async def get_tags():
    try:
        tags =  client.tags.list()
        if not tags:
            return Response(status_code=204)
        return [map_tag_to_tag_response(tag) for tag in tags]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tags/{tag_id}")
async def get_tag(tag_id: str):
    try:
        tag: Tag =  client.tags.retrieve(tag_id=tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        return map_tag_to_tag_response(tag)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tags")
async def create_tag(tag_data: CreateTagRequest):
    try:
        tag: Tag =  client.tags.create(**tag_data.model_dump())
        return map_tag_to_tag_response(tag)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.patch("/tags/{tag_id}")
async def update_tag(tag_id: str, tag_data: UpdateTagRequest):
    try:
        tag: Tag =  client.tags.retrieve(tag_id=tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        updated_tag =  client.tags.update(tag_id=tag_id, **tag_data.model_dump())
        return map_tag_to_tag_response(updated_tag)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tags/{tag_id}")
async def delete_tag(tag_id: str):
    try:
        tag: Tag =  client.tags.retrieve(tag_id=tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        client.tags.delete(tag_id=tag_id)
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ----------------------- TERMS ----------------------------

@app.get("/terms")
async def get_terms():
    try:
        terms =  client.glossary.list_terms()
        if not terms:
            return Response(status_code=204)
        return [map_term_to_term_response(term) for term in terms]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/terms/{term_id}")
async def get_term(term_id: str):
    try:
        term: Term =  client.glossary.retrieve_term(term_id=term_id)
        if not term:
            raise HTTPException(status_code=404, detail="Term not found")
        return map_term_to_term_response(term)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/terms")
async def create_term(term_data: CreateTermRequest):
    try:
        term: Term =  client.glossary.create_term(**term_data.model_dump())
        return map_term_to_term_response(term)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/terms/{term_id}")
async def update_term(term_id: str, term_data: UpdateTermRequest):
    try:
        term: Term =  client.glossary.retrieve_term(term_id=term_id)
        if not term:
            raise HTTPException(status_code=404, detail="Term not found")
        updated_term =  client.glossary.update_term(term_id=term_id, **term_data.model_dump())
        return map_term_to_term_response(updated_term)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/terms/{term_id}")
async def delete_term(term_id: str):
    try:
        term: Term =  client.glossary.retrieve_term(term_id=term_id)
        if not term:
            raise HTTPException(status_code=404, detail="Term not found")
        client.glossary.delete_term(term_id=term_id)
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------ GUIDELINES ----------------------------

@app.get("/guidelines")
async def get_guidelines():
    try:
        guidelines =  client.guidelines.list()
        if not guidelines:
            return Response(status_code=204)
        return [map_guideline_to_guideline_response(guideline) for guideline in guidelines]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/guidelines/{guideline_id}")
async def get_guideline(guideline_id: str):
    try:
        guideline: Guideline =  client.guidelines.retrieve(guideline_id=guideline_id)
        if not guideline:
            raise HTTPException(status_code=404, detail="Guideline not found")
        return map_guideline_to_guideline_response(guideline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/guidelines")
async def create_guideline(guideline_data: CreateGuidelineRequest):
    try:
        guideline: Guideline =  client.guidelines.create(**guideline_data.model_dump())
        return map_guideline_to_guideline_response(guideline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/guidelines/{guideline_id}")
async def update_guideline(guideline_id: str, guideline_data: UpdateGuidelineRequest):
    try:
        guideline: Guideline =  client.guidelines.retrieve(guideline_id=guideline_id)
        if not guideline:
            raise HTTPException(status_code=404, detail="Guideline not found")
        updated_guideline =  client.guidelines.update(guideline_id=guideline_id, **guideline_data.model_dump())
        return map_guideline_to_guideline_response(updated_guideline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/guidelines/{guideline_id}")
async def delete_guideline(guideline_id: str):
    try:
        guideline: Guideline =  client.guidelines.retrieve(guideline_id=guideline_id)
        if not guideline:
            raise HTTPException(status_code=404, detail="Guideline not found")
        client.guidelines.delete(guideline_id=guideline_id)
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------ JOURNEYS ----------------------------

@app.get("/journeys")
async def get_journeys():
    try:
        journeys =  client.journeys.list()
        if not journeys:
            return Response(status_code=204)
        return [map_journey_to_journey_response(journey) for journey in journeys]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/journeys/{journey_id}")
async def get_journey(journey_id: str):
    try:
        journey: Journey =  client.journeys.retrieve(journey_id=journey_id)
        if not journey:
            return Response(status_code=204)
        return map_journey_to_journey_response(journey)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/journeys")
async def create_journey(journey_data: CreateJourneyRequest):
    try:
        journey: Journey =  client.journeys.create(**journey_data.model_dump())
        return map_journey_to_journey_response(journey)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/journeys/{journey_id}")
async def update_journey(journey_id: str, journey_data: UpdateJourneyRequest):
    try:
        journey: Journey =  client.journeys.retrieve(journey_id=journey_id)
        if not journey:
            return Response(status_code=204)
        updated_journey =  client.journeys.update(journey_id=journey_id, **journey_data.model_dump())
        return map_journey_to_journey_response(updated_journey)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/journeys/{journey_id}")
async def delete_journey(journey_id: str):
    try:
        journey: Journey =  client.journeys.retrieve(journey_id=journey_id)
        if not journey:
            return Response(status_code=204)
        client.journeys.delete(journey_id=journey_id)
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

uvicorn.run(app, host="0.0.0.0", port=6001)