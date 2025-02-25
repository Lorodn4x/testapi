from fastapi import APIRouter, HTTPException
from ..schemas.chat import (
    ChatCompletionRequest, ChatCompletionResponse, ChatMessage,
    Tool, ToolCall, Function
)
from ..core.config import settings
import httpx
import json
import time
import uuid
from typing import Optional, Dict, Any, List

router = APIRouter()

def prepare_messages_with_function_calling(
    messages: list[ChatMessage],
    functions: Optional[list] = None,
    function_call: Optional[Dict[str, Any]] = None,
    tools: Optional[List[Tool]] = None,
    tool_choice: Optional[Dict[str, Any]] = None
) -> list[Dict[str, Any]]:
    """Prepare messages for Pollinations API with function/tool calling support"""
    
    # Convert tools to functions if present
    if tools and not functions:
        functions = []
        for tool in tools:
            if tool.type == "function":
                functions.append(Function(
                    name=tool.function.name,
                    description=tool.function.description,
                    parameters=tool.function.parameters
                ))
    
    # Add system message for function calling if functions are present
    if (functions or tools) and not any(msg.role == "system" for msg in messages):
        messages.insert(0, ChatMessage(
            role="system",
            content=settings.FUNCTION_CALLING_SYSTEM_PROMPT
        ))
    
    # Convert messages to format expected by Pollinations
    formatted_messages = []
    for msg in messages:
        message_dict = {
            "role": msg.role,
            "content": msg.content or ""
        }
        if msg.name:
            message_dict["name"] = msg.name
        if msg.function_call:
            # Convert function call arguments to string if they're not already
            if isinstance(msg.function_call.get("arguments"), (dict, list)):
                msg.function_call["arguments"] = json.dumps(msg.function_call["arguments"])
            message_dict["function_call"] = msg.function_call
        if msg.tool_calls:
            message_dict["tool_calls"] = []
            for tool_call in msg.tool_calls:
                formatted_tool_call = {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.get("name", ""),
                        "arguments": json.dumps(tool_call.function.get("parameters", {}))
                    }
                }
                message_dict["tool_calls"].append(formatted_tool_call)
        if msg.tool_call_id:
            message_dict["tool_call_id"] = msg.tool_call_id
        formatted_messages.append(message_dict)
    
    return formatted_messages

def extract_function_or_tool_call(content: str) -> tuple[Optional[Dict[str, Any]], Optional[List[ToolCall]]]:
    """Extract function call or tool calls from content"""
    try:
        # Try to parse the content as JSON
        data = json.loads(content)
        if isinstance(data, dict):
            # Check for function call
            if "function_call" in data:
                function_call = data["function_call"]
                # Ensure arguments is a string
                if isinstance(function_call.get("parameters"), (dict, list)):
                    function_call["arguments"] = json.dumps(function_call["parameters"])
                    function_call.pop("parameters", None)
                return function_call, None
            # Check for direct function call format
            if "name" in data and "parameters" in data:
                # Convert parameters to arguments string
                return {
                    "name": data["name"],
                    "arguments": json.dumps(data["parameters"])
                }, None
            # Check for tool calls
            if "tool_calls" in data:
                tool_calls = []
                for call in data["tool_calls"]:
                    # Ensure function arguments is a string
                    if "function" in call:
                        if isinstance(call["function"].get("parameters"), (dict, list)):
                            call["function"]["arguments"] = json.dumps(call["function"]["parameters"])
                            call["function"].pop("parameters", None)
                    tool_calls.append(ToolCall(
                        id=call.get("id", str(uuid.uuid4())),
                        type=call.get("type", "function"),
                        function=call["function"]
                    ))
                return None, tool_calls
        return None, None
    except json.JSONDecodeError:
        # If content is not JSON, try to extract function call using regex
        import re
        match = re.search(r'{\s*"name":\s*"([^"]+)",\s*"parameters":\s*({[^}]+})\s*}', content)
        if match:
            try:
                name = match.group(1)
                parameters = json.loads(match.group(2))
                return {
                    "name": name,
                    "arguments": json.dumps(parameters)
                }, None
            except:
                pass
        return None, None

def serialize_functions_or_tools(
    functions: Optional[List[Function]] = None,
    tools: Optional[List[Tool]] = None
) -> str:
    """Serialize functions or tools to JSON string"""
    if tools:
        serialized_items = []
        for tool in tools:
            if tool.type == "function":
                serialized_item = {
                    "type": "function",
                    "function": {
                        "name": tool.function.name,
                        "description": tool.function.description,
                        "parameters": {
                            "type": tool.function.parameters.type,
                            "description": tool.function.parameters.description,
                            "properties": tool.function.parameters.properties,
                            "required": tool.function.parameters.required
                        }
                    }
                }
                if tool.function.parameters.enum:
                    serialized_item["function"]["parameters"]["enum"] = tool.function.parameters.enum
                if tool.function.parameters.items:
                    serialized_item["function"]["parameters"]["items"] = tool.function.parameters.items
                serialized_items.append(serialized_item)
        return json.dumps(serialized_items, indent=2)
    
    elif functions:
        serialized_items = []
        for func in functions:
            serialized_item = {
                "name": func.name,
                "description": func.description,
                "parameters": {
                    "type": func.parameters.type,
                    "description": func.parameters.description,
                    "properties": func.parameters.properties,
                    "required": func.parameters.required
                }
            }
            if func.parameters.enum:
                serialized_item["parameters"]["enum"] = func.parameters.enum
            if func.parameters.items:
                serialized_item["parameters"]["items"] = func.parameters.items
            serialized_items.append(serialized_item)
        return json.dumps(serialized_items, indent=2)
    
    return "[]"

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    """Create a chat completion with function/tool calling support"""
    
    # Prepare messages with function/tool calling support
    messages = prepare_messages_with_function_calling(
        request.messages,
        request.functions,
        request.function_call,
        request.tools,
        request.tool_choice
    )
    
    # Prepare the request to Pollinations
    pollinations_request = {
        "messages": messages,
        "model": request.model,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "n": request.n,
        "stream": request.stream,
        "stop": request.stop,
        "max_tokens": request.max_tokens,
        "presence_penalty": request.presence_penalty,
        "frequency_penalty": request.frequency_penalty,
    }
    
    # If functions or tools are present, add them to the prompt
    if request.functions or request.tools:
        items_str = serialize_functions_or_tools(request.functions, request.tools)
        system_message = f"""Available {'tools' if request.tools else 'functions'}:
{items_str}

Instructions:
1. If a {'tool' if request.tools else 'function'} is needed to answer the user's request, use it.
2. Return your response in JSON format.
3. Only use {'tools' if request.tools else 'functions'} when necessary and relevant.
4. Use the exact format:
   For functions: {{"function_call": {{"name": "function_name", "arguments": "{{\\"param1\\": \\"value1\\"}}"}}}}
   For tools: {{"tool_calls": [{{"id": "call_1", "type": "function", "function": {{"name": "tool_name", "arguments": "{{\\"param1\\": \\"value1\\"}}"}}}}]}}"""
        
        pollinations_request["messages"].insert(0, {
            "role": "system",
            "content": system_message
        })
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.POLLINATIONS_BASE_URL}/",
                json=pollinations_request,
                timeout=30.0
            )
            print("DEBUG: Pollinations Request:", pollinations_request)
            print("DEBUG: Raw Pollinations Response:", response.text)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error from Pollinations API: {response.text}"
                )
            
            content = response.text
            
            # Check for function or tool calls in the response
            function_call, tool_calls = extract_function_or_tool_call(content)
            
            # If we got a function call or tool calls, use them directly
            if function_call or tool_calls:
                content = None
            else:
                # Try to parse as regular JSON response
                try:
                    pollinations_response = response.json()
                    if isinstance(pollinations_response, dict) and "choices" in pollinations_response:
                        content = pollinations_response.get("choices", [{}])[0].get("message", {}).get("content", content)
                except json.JSONDecodeError:
                    # If not JSON, use the raw content
                    pass
            
            # Prepare the OpenAI-compatible response
            chat_response = ChatCompletionResponse(
                id=f"chatcmpl-{int(time.time()*1000)}",
                object="chat.completion",
                created=int(time.time()),
                model=request.model,
                choices=[{
                    "index": 0,
                    "message": ChatMessage(
                        role="assistant",
                        content=content,
                        function_call=function_call,
                        tool_calls=tool_calls
                    ),
                    "finish_reason": "tool_calls" if tool_calls else "function_call" if function_call else "stop"
                }],
                usage={
                    "prompt_tokens": len(str(messages)) // 4,  # Approximate
                    "completion_tokens": len(content or "") // 4,  # Approximate
                    "total_tokens": (len(str(messages)) + len(content or "")) // 4
                }
            )
            
            return chat_response
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Pollinations API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 