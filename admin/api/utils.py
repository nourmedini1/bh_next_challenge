from parlant.sdk import Agent,Tag,Term,Guideline,Journey
from models import * 


def map_agent_to_agent_response(agent: Agent) -> AgentResponse:
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        tags=agent.tags,
    )

def map_tag_to_tag_response(tag: Tag) -> TagResponse:
    return TagResponse(
        id=tag.id,
        name=tag.name,
    )

def map_term_to_term_response(term: Term) -> TermResponse:
    return TermResponse(
        id=term.id,
        name=term.name,
        description=term.description,
        synonyms=term.synonyms,
        tags=term.tags
    )

def map_guideline_to_guideline_response(guideline: Guideline) -> GuidelineResponse:
    return GuidelineResponse(
        id=guideline.id,
        condition=guideline.condition,
        action=guideline.action,
        tags=guideline.tags,
        metadata=guideline.metadata,
    )

def map_journey_to_journey_response(journey: Journey) -> JourneyResponse:
    return JourneyResponse(
        id=journey.id,
        title=journey.title,
        description=journey.description,
        conditions=journey.conditions,
        tags=journey.tags,
    )
