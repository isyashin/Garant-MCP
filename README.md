# Garant MCP Server

Model Context Protocol (MCP) сервер для доступа к API Гарант Коннект.

## Возможности

- **Поиск документов** — поиск по базе Гаранта с поддержкой query language
- **Информация о документах** — метаданные, статус, актуальность
- **Экспорт** — RTF, PDF, ODT, HTML форматы
- **Мониторинг изменений** — отслеживание изменений в документах
- **PRIME новости** — лента новостей по категориям
- **Судебная практика** — поиск в системе "Сутяжник"
- **Постановка ссылок** — автоматическая простановка ссылок на законы
- **Кэширование** — кэширование запросов для экономии лимитов

## Установка (Windows)

### 1. Клонирование репозитория

```powershell
git clone https://github.com/yourusername/garant-mcp.git
cd garant-mcp
```

### 2. Установка зависимостей

```powershell
.\scripts\install.ps1
```

### 3. Настройка

Отредактируйте файл `.env`:

```env
GARANT_TOKEN=your_token_here
LOG_LEVEL=INFO
```

## Запуск

```powershell
.\scripts\run.ps1
```

Сервер запускается с STDIO транспортом для работы с opencode.

## Тестирование

```powershell
.\scripts\test.ps1
```

## Инструменты (Tools)

| Инструмент | Описание | Лимит |
|-----------|----------|-------|
| `search_documents` | Поиск документов | Бесплатно |
| `get_document_info` | Информация о документе | 300/мес |
| `get_document_snippets` | Фрагменты текста | Бесплатно |
| `create_legal_document` | Постановка ссылок | 1000/мес |
| `check_document_updates` | Мониторинг изменений | 1000/мес |
| `export_document_rtf` | Экспорт в RTF | 30/мес |
| `export_document_pdf` | Экспорт в PDF | 30/мес |
| `export_document_odt` | Экспорт в ODT | 30/мес |
| `export_document_html` | Экспорт в HTML | 30/мес |
| `export_block_html` | Экспорт блока HTML | 30/мес |
| `get_prime_categories` | Категории PRIME | Бесплатно |
| `get_prime_news` | Лента PRIME | Бесплатно |
| `search_judicial_practice` | Судебная практика | Бесплатно |
| `get_usage_limits` | Проверка лимитов | Бесплатно |
| `download_image` | Скачать изображение | 30/мес |
| `download_formula` | Скачать формулу | 30/мес |

## Ресурсы (Resources)

| Ресурс | Описание |
|--------|----------|
| `garant://document/{topic}` | Информация о документе |
| `garant://limits` | Текущие лимиты |
| `garant://prime/categories` | Категории PRIME |

## Промпты (Prompts)

| Промпт | Описание |
|--------|----------|
| `legal_complaint` | Шаблон жалобы |
| `contract_review` | Проверка договора |
| `document_analysis` | Анализ документа |

## Примеры использования

### Поиск документов

```python
result = await search_documents(
    text="налог",
    env="internet",
    sort=0,
    page=1
)
```

### Получение информации о документе

```python
result = await get_document_info(12138291)  # ЖК РФ
```

### Создание документа со ссылками

```python
html = await create_legal_document(
    text="В соответствии со статьей 36 ЖК РФ..."
)
```

### Экспорт документа

```python
path = await export_document_pdf(12138291)
print(f"PDF сохранен: {path}")
```

### Проверка изменений

```python
result = await check_document_updates(
    topics=[12138291, 12148944],
    mod_date="2025-01-01",
    need_events=True
)
```

## Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `GARANT_TOKEN` | API токен Гарант | - |
| `GARANT_BASE_URL` | URL API | https://api.garant.ru/v2 |
| `LOG_LEVEL` | Уровень логирования | INFO |
| `CACHE_TTL_TOPIC` | TTL кэша topic (сек) | 7200 |
| `CACHE_TTL_LIMITS` | TTL кэша лимитов (сек) | 300 |
| `CACHE_TTL_PRIME` | TTL кэша PRIME (сек) | 3600 |
| `CACHE_TTL_SNIPPETS` | TTL кэша snippets (сек) | 1800 |
| `CACHE_TTL_SEARCH` | TTL кэша поиска (сек) | 900 |
| `CACHE_DIR` | Директория кэша | .cache |
| `EXPORT_DIR` | Директория экспорта | exports |

### Конфигурация opencode

Добавьте в `opencode.json`:

```json
{
  "mcp": {
    "garant": {
      "type": "local",
      "command": ["python", "-m", "garant_mcp.server"],
      "enabled": true,
      "env": {
        "GARANT_TOKEN": "your_token"
      }
    }
  }
}
```

## Структура проекта

```
garant-mcp/
├── src/
│   └── garant_mcp/
│       ├── __init__.py
│       ├── server.py          # Точка входа
│       ├── client.py          # HTTP клиент
│       ├── cache.py           # Кэширование
│       ├── config.py          # Конфигурация
│       ├── tools.py           # MCP Tools
│       ├── resources.py       # MCP Resources
│       └── prompts.py         # MCP Prompts
├── tests/
│   ├── conftest.py
│   ├── test_client.py
│   └── test_tools.py
├── scripts/
│   ├── install.ps1           # Установка
│   ├── run.ps1               # Запуск
│   └── test.ps1              # Тесты
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── README.md
```

## Логирование

Логи сохраняются в директории `logs/`:
- `garant-mcp.log` — основной лог
- Ротация: 10 файлов по 10MB

## Разработка

### Добавление нового инструмента

1. Добавьте функцию в `src/garant_mcp/tools.py`
2. Зарегистрируйте в `src/garant_mcp/server.py`
3. Добавьте тесты в `tests/`
4. Обновите README

### Запуск тестов

```powershell
pytest tests/ -v
```

### Проверка типов

```powershell
mypy src/
```

### Форматирование кода

```powershell
black src/ tests/
ruff check src/ tests/
```

## Лицензия

MIT

## Поддержка

При возникновении проблем создайте issue в репозитории.
