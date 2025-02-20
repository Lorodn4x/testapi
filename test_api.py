from openai import OpenAI
import json

def test_function_calling():
    # Инициализация клиента с нашим локальным API
    client = OpenAI(
        api_key="not-needed",  # API key не требуется, но должен быть указан
        base_url="http://localhost:8000/v1"  # URL нашего локального API
    )

    # Пример функции для получения погоды
    functions = [{
        "name": "get_weather",
        "description": "Получить информацию о погоде в указанном месте",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Город и страна"
                }
            },
            "required": ["location"]
        }
    }]

    try:
        # Отправляем запрос
        response = client.chat.completions.create(
            model="openai",
            messages=[
                {"role": "user", "content": "Какая погода в Москве?"}
            ],
            functions=functions
        )
        
        # Выводим результат
        print("\nAPI Response:")
        print(f"Role: {response.choices[0].message.role}")
        print(f"Content: {response.choices[0].message.content}")
        print(f"Function call: {response.choices[0].message.function_call}")
        if response.choices[0].message.function_call:
            print(f"Function arguments type: {type(response.choices[0].message.function_call.arguments)}")
        print(f"Finish reason: {response.choices[0].finish_reason}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_tool_calling():
    # Инициализация клиента с нашим локальным API
    client = OpenAI(
        api_key="not-needed",
        base_url="http://localhost:8000/v1"
    )

    # Пример инструмента для получения погоды
    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Получить информацию о погоде в указанном месте",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Город и страна"
                    }
                },
                "required": ["location"]
            }
        }
    }]

    try:
        # Отправляем запрос
        response = client.chat.completions.create(
            model="openai",
            messages=[
                {"role": "user", "content": "Какая погода в Санкт-Петербурге?"}
            ],
            tools=tools
        )
        
        # Выводим результат
        print("\nTool API Response:")
        print(f"Role: {response.choices[0].message.role}")
        print(f"Content: {response.choices[0].message.content}")
        print(f"Tool calls: {response.choices[0].message.tool_calls}")
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                print(f"Tool arguments type: {type(tool_call.function.arguments)}")
        print(f"Finish reason: {response.choices[0].finish_reason}")
        
        # Тестируем обработку ответа функции
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            response = client.chat.completions.create(
                model="openai",
                messages=[
                    {"role": "user", "content": "Какая погода в Санкт-Петербурге?"},
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                        ]
                    },
                    {
                        "role": "tool",
                        "content": json.dumps({"temperature": 20, "conditions": "sunny"}),
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name
                    }
                ],
                tools=tools
            )
            print("\nTool Response Processing:")
            print(f"Role: {response.choices[0].message.role}")
            print(f"Content: {response.choices[0].message.content}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_simple_completion():
    # Тест простого запроса без function calling
    client = OpenAI(
        api_key="not-needed",
        base_url="http://localhost:8000/v1"
    )

    try:
        response = client.chat.completions.create(
            model="openai",
            messages=[
                {"role": "user", "content": "Привет! Как дела?"}
            ]
        )
        
        print("\nSimple Completion Response:")
        print(f"Role: {response.choices[0].message.role}")
        print(f"Content: {response.choices[0].message.content}")
        print(f"Finish reason: {response.choices[0].finish_reason}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_models_endpoint():
    # Тест endpoint /models
    client = OpenAI(
        api_key="not-needed",
        base_url="http://localhost:8000/v1"
    )

    try:
        models = client.models.list()
        
        print("\nAvailable Models:")
        for model in models.data:
            print(f"- {model.id}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI-Compatible Pollinations API")
    print("=========================================")
    
    print("\n1. Testing function calling...")
    function_test = test_function_calling()
    
    print("\n2. Testing tool calling...")
    tool_test = test_tool_calling()
    
    print("\n3. Testing simple completion...")
    completion_test = test_simple_completion()
    
    print("\n4. Testing models endpoint...")
    models_test = test_models_endpoint()
    
    print("\nTest Results:")
    print(f"Function calling test: {'✓' if function_test else '✗'}")
    print(f"Tool calling test: {'✓' if tool_test else '✗'}")
    print(f"Simple completion test: {'✓' if completion_test else '✗'}")
    print(f"Models endpoint test: {'✓' if models_test else '✗'}") 