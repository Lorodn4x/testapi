from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import httpx
import json
from ..core.config import settings

router = APIRouter()

class ModelPermission(BaseModel):
    id: str = "modelperm-000000000000000000000000"
    object: str = "model_permission"
    created: int = 1677610602
    allow_create_engine: bool = True
    allow_sampling: bool = True
    allow_logprobs: bool = True
    allow_search_indices: bool = True
    allow_view: bool = True
    allow_fine_tuning: bool = True
    organization: str = "*"
    group: str | None = None
    is_blocking: bool = False

class Model(BaseModel):
    id: str
    object: str = "model"
    created: int = 1677610602
    owned_by: str = "pollinations"
    permission: List[ModelPermission] = [ModelPermission()]
    root: str | None = None
    parent: str | None = None

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[Model]

@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """List available models"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.POLLINATIONS_BASE_URL}/models",
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error fetching models from Pollinations API: {response.text}"
                )
            
            try:
                pollinations_models = response.json()
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=500,
                    detail=f"Invalid JSON response from Pollinations API: {response.text}"
                )
            
            if not isinstance(pollinations_models, (list, dict)):
                raise HTTPException(
                    status_code=500,
                    detail=f"Unexpected response format from Pollinations API: {pollinations_models}"
                )
            
            # Handle both list and dict responses
            if isinstance(pollinations_models, dict):
                model_ids = list(pollinations_models.keys())
            else:
                model_ids = pollinations_models
            
            # Convert Pollinations models to OpenAI format
            models = []
            for model_id in model_ids:
                if isinstance(model_id, str):
                    models.append(Model(id=model_id))
            
            return ModelsResponse(data=models)
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Pollinations API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 