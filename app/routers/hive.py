
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.hive.hive_mind import hive_mind, HiveMessage

router = APIRouter()

class TopicRequest(BaseModel):
    topic: str

class StartCouncilResponse(BaseModel):
    session_id: str

class CouncilResponse(BaseModel):
    messages: List[HiveMessage]

@router.post("/council", response_model=StartCouncilResponse)
async def start_council(request: TopicRequest):
    session_id = await hive_mind.start_council(request.topic)
    return StartCouncilResponse(session_id=session_id)

@router.get("/council/{session_id}/poll", response_model=CouncilResponse)
async def poll_council(session_id: str):
    new_messages = await hive_mind.process_turn(session_id)
    return CouncilResponse(messages=new_messages)
