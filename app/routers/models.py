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
                try:
                    pollinations_models = response.json()
                    print("Parsed Models:", pollinations_models)
                except json.JSONDecodeError:
                    # Try to fix malformed JSON manually
                    fixed_json = "[" + response.text.replace("}{", "},{") + "]"
                    try:
                        pollinations_models = json.loads(fixed_json)
                    except Exception:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Failed to parse fixed JSON response: {response.text}"
                        )
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
            formatted_models = []
            for model_data in pollinations_models:
                if isinstance(model_data, dict):
                    formatted_models.append({
                        "id": model_data.get("name", "unknown"),  # Assign 'id' from 'name'
                        "name": model_data.get("name", "unknown"),
                        "type": model_data.get("type", "unknown"),
                        "censored": model_data.get("censored", False),
                        "description": model_data.get("description", ""),
                        "baseModel": model_data.get("baseModel", False),
                        "reasoning": model_data.get("reasoning", None),
                        "vision": model_data.get("vision", None),
                        "provider": model_data.get("provider", None),
                    })
            return {"data": formatted_models}
            
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