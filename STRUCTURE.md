# Структура проекта

```
api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Основной файл приложения
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Конфигурация приложения
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py           # Обработчик чат-запросов и function calling
│   │   └── models.py         # Обработчик запросов к моделям
│   └── schemas/
│       ├── __init__.py
│       └── chat.py           # Pydantic модели для валидации
├── tests/
│   ├── __init__.py
│   └── test_api.py          # Тесты API
├── .env                     # Переменные окружения
├── .gitignore              # Игнорируемые файлы Git
├── requirements.txt        # Зависимости проекта
├── README.md              # Основная документация
├── IMPLEMENTATION.md      # Детальная документация реализации
└── STRUCTURE.md          # Описание структуры проекта (этот файл)
```

## Описание компонентов

### Основные файлы

- `main.py` - Входная точка приложения, настройка FastAPI
- `requirements.txt` - Список зависимостей с версиями
- `.env` - Конфигурация окружения
- `README.md` - Основная документация проекта
- `IMPLEMENTATION.md` - Подробная документация реализации

### Директории

#### app/

Основная директория приложения, содержащая всю логику.

#### app/core/

Ядро приложения:
- `config.py` - Настройки приложения, переменные окружения

#### app/routers/

Маршрутизаторы API:
- `chat.py` - Обработка чат-запросов, function calling и tool calling
- `models.py` - Работа со списком моделей

#### app/schemas/

Схемы данных:
- `chat.py` - Pydantic модели для валидации запросов и ответов

#### tests/

Тесты:
- `test_api.py` - Тесты всех endpoint'ов и функциональности

## Ключевые компоненты

### Маршрутизация (app/routers/)

- `chat.py`:
  - POST `/v1/chat/completions`
  - Обработка function calling
  - Обработка tool calling
  - Форматирование ответов

- `models.py`:
  - GET `/v1/models`
  - Получение списка моделей
  - Форматирование в OpenAI формат

### Схемы данных (app/schemas/)

- `chat.py`:
  - `ChatMessage`
  - `ChatCompletionRequest`
  - `ChatCompletionResponse`
  - `Function`
  - `Tool`
  - `ToolCall`

### Конфигурация (app/core/)

- `config.py`:
  - Настройки Pollinations API
  - Системные промпты
  - Параметры приложения

## Зависимости

Основные зависимости проекта:
```
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.3
python-dotenv>=1.0.0
httpx>=0.26.0
python-multipart>=0.0.6
typing-extensions>=4.9.0
```

## Рабочий процесс

1. Запрос поступает через FastAPI endpoint
2. Валидируется через Pydantic модели
3. Обрабатывается соответствующим маршрутизатором
4. Преобразуется в формат Pollinations API
5. Отправляется запрос к Pollinations
6. Ответ преобразуется обратно в формат OpenAI
7. Возвращается клиенту

## Расширение проекта

При добавлении новой функциональности:

1. Создайте новые схемы в `app/schemas/`
2. Добавьте новые маршруты в `app/routers/`
3. Обновите конфигурацию в `app/core/config.py`
4. Добавьте тесты в `tests/test_api.py`
5. Обновите документацию 