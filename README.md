# OpenAI-Compatible Pollinations.AI Proxy

Полностью совместимый с OpenAI API прокси-сервер для Pollinations.AI с поддержкой Function Calling и Tool Calling.

## Возможности

- ✓ Полная совместимость с OpenAI API
- ✓ Поддержка Function Calling (старый формат)
- ✓ Поддержка Tool Calling (новый формат)
- ✓ Стандартные чат-комплишены
- ✓ Endpoint для получения списка моделей
- ✓ Обработка ошибок и валидация
- ✓ Готовность к production

## Установка

1. Клонируйте репозиторий:
```bash
git clone [url-репозитория]
cd [имя-директории]
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения:
```bash
POLLINATIONS_BASE_URL=https://text.pollinations.ai
```

4. Запустите сервер:
```bash
uvicorn app.main:app --reload
```

## Использование

### Простой чат-запрос

```python
from openai import OpenAI

client = OpenAI(
    api_key="not-needed",  # API ключ не требуется, но должен быть указан
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="openai",
    messages=[
        {"role": "user", "content": "Привет! Как дела?"}
    ]
)

print(response.choices[0].message.content)
```

### Использование Function Calling

```python
response = client.chat.completions.create(
    model="openai",
    messages=[
        {"role": "user", "content": "Какая погода в Москве?"}
    ],
    functions=[{
        "name": "get_weather",
        "description": "Получить информацию о погоде",
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
)

print(response.choices[0].message.function_call)
```

### Использование Tool Calling

```python
response = client.chat.completions.create(
    model="openai",
    messages=[
        {"role": "user", "content": "Какая погода в Санкт-Петербурге?"}
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Получить информацию о погоде",
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
)

if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    # Обработка вызова инструмента
    print(tool_call.function.name)
    print(tool_call.function.arguments)
```

### Получение списка моделей

```python
models = client.models.list()
for model in models.data:
    print(model.id)
```

## API Endpoints

- `POST /v1/chat/completions` - Чат-комплишены с поддержкой функций и инструментов
- `GET /v1/models` - Список доступных моделей
- `GET /v1/health` - Проверка работоспособности API

## Особенности реализации

- Автоматическая конвертация между форматами functions и tools
- Поддержка как JSON, так и текстовых ответов
- Корректная обработка ошибок и валидация
- Поддержка multiple tool calls
- Правильная передача tool_call_id
- Эмуляция function calling через промпты

## Зависимости

```
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.3
python-dotenv>=1.0.0
httpx>=0.26.0
python-multipart>=0.0.6
typing-extensions>=4.9.0
```

## Тестирование

Запустите тесты:
```bash
python test_api.py
```

Тесты проверяют:
- Function Calling
- Tool Calling
- Simple Completions
- Models Endpoint

## Ограничения

- Нет нативной поддержки function calling в Pollinations API
- Упрощённый подсчёт токенов
- Базовая поддержка streaming

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Лицензия

MIT

## Документация

Подробная документация о реализации доступна в файле [IMPLEMENTATION.md](IMPLEMENTATION.md). 