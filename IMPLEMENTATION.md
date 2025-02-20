# Реализация OpenAI-совместимого API с поддержкой Function Calling и Tool Calling

## Обзор

Мы создали полностью совместимый с OpenAI API сервис, который работает поверх Pollinations.AI. Наша реализация поддерживает:

- Function Calling (старый формат)
- Tool Calling (новый формат)
- Стандартные чат-комплишены
- Endpoint для получения списка моделей
- Полную совместимость с OpenAI SDK

## Архитектура

### Основные компоненты

1. **FastAPI приложение** (`app/main.py`):
   - Основной входной точкой является FastAPI приложение
   - Поддержка CORS для веб-клиентов
   - Маршрутизация запросов к соответствующим обработчикам

2. **Схемы данных** (`app/schemas/chat.py`):
   - Pydantic модели для валидации запросов и ответов
   - Полная совместимость с форматами OpenAI API
   - Поддержка как функций, так и инструментов

3. **Роутеры** (`app/routers/`):
   - `chat.py` - обработка чат-комплишенов и вызовов функций
   - `models.py` - получение списка доступных моделей

4. **Конфигурация** (`app/core/config.py`):
   - Настройки приложения
   - Системные промпты для function/tool calling

## Ключевые особенности реализации

### 1. Function Calling

```python
# Формат запроса
{
    "model": "openai",
    "messages": [{"role": "user", "content": "Какая погода в Москве?"}],
    "functions": [{
        "name": "get_weather",
        "description": "Получить информацию о погоде",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }]
}

# Формат ответа
{
    "function_call": {
        "name": "get_weather",
        "arguments": "{\"location\": \"Москва, Россия\"}"
    }
}
```

### 2. Tool Calling

```python
# Формат запроса
{
    "model": "openai",
    "messages": [{"role": "user", "content": "Какая погода в Москве?"}],
    "tools": [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Получить информацию о погоде",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                }
            }
        }
    }]
}

# Формат ответа
{
    "tool_calls": [{
        "id": "call_1",
        "type": "function",
        "function": {
            "name": "get_weather",
            "arguments": "{\"location\": \"Москва, Россия\"}"
        }
    }]
}
```

## Особенности обработки

1. **Преобразование форматов**:
   - Автоматическая конвертация tools в functions для Pollinations
   - Правильное форматирование аргументов как JSON строк
   - Поддержка обоих форматов в одном API

2. **Обработка ответов**:
   - Извлечение вызовов функций из ответов
   - Поддержка как JSON, так и текстовых ответов
   - Корректная обработка ошибок

3. **Обработка инструментов**:
   - Поддержка multiple tool calls
   - Правильная передача tool_call_id
   - Корректная обработка ответов от инструментов

## Пример использования

```python
from openai import OpenAI

client = OpenAI(
    api_key="not-needed",
    base_url="http://localhost:8000/v1"
)

# Использование Tool Calling
response = client.chat.completions.create(
    model="openai",
    messages=[
        {"role": "user", "content": "Какая погода в Москве?"}
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Получить информацию о погоде",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                }
            }
        }
    }]
)

# Обработка ответа инструмента
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    response = client.chat.completions.create(
        model="openai",
        messages=[
            {"role": "user", "content": "Какая погода в Москве?"},
            {
                "role": "assistant",
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
        ]
    )
```

## Тестирование

Реализованы тесты для всех основных функций:

1. **Function Calling Test**:
   - Проверка формата запроса
   - Проверка формата ответа
   - Проверка типов аргументов

2. **Tool Calling Test**:
   - Проверка формата запроса
   - Проверка формата ответа
   - Проверка обработки tool_call_id
   - Проверка обработки ответов инструментов

3. **Simple Completion Test**:
   - Проверка обычных чат-ответов
   - Проверка форматирования ответов

4. **Models Endpoint Test**:
   - Проверка получения списка моделей
   - Проверка формата ответа

## Ограничения и особенности

1. **Pollinations API**:
   - Нет нативной поддержки function calling
   - Используем промпты для эмуляции функциональности
   - Возможны небольшие отклонения в формате ответов

2. **Токенизация**:
   - Упрощённый подсчёт токенов
   - Возможны неточности в usage статистике

3. **Streaming**:
   - Базовая поддержка streaming
   - Может требовать дополнительной настройки

## Дальнейшие улучшения

1. **Производительность**:
   - Кэширование ответов
   - Оптимизация обработки запросов
   - Улучшение подсчёта токенов

2. **Функциональность**:
   - Поддержка параллельных вызовов инструментов
   - Улучшенная обработка ошибок
   - Расширенная валидация запросов

3. **Мониторинг**:
   - Логирование использования
   - Метрики производительности
   - Отслеживание ошибок

## Заключение

Наша реализация предоставляет полностью совместимый с OpenAI API интерфейс, работающий поверх Pollinations.AI. Поддержка как старого (functions), так и нового (tools) форматов делает API универсальным решением для различных приложений. 