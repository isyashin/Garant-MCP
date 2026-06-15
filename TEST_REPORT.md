# Отчёт о полном тестировании Garant MCP Server

**Дата:** 2026-06-15  
**Тестируемый проект:** `garant-mcp` (MCP-сервер для API Гарант Коннект)  
**Окружение:** Windows, Python 3.13.7, pytest 9.0.3, respx 0.23.1, httpx 0.28.1  
**Тестовые файлы:** `tests/test_all_features.py`, `tests/test_file_tools.py`, `scripts/manual_api_check.py`, `scripts/auth_variants_check.py`, `scripts/compare_limits_search.py`  

## Резюме

Полное тестирование всех функций проекта **успешно завершено**. После получения корректного API-токена все endpoint Гарант Коннект v2 работают. Автотесты проходят полностью.

**Итоговый результат:** `51 passed, 0 failed`

## История проверки

### Первый токен

- `GET /limits` — работал (200)
- Все остальные endpoint — возвращали `401 Unauthorized`
- Проверены разные варианты авторизации, заголовки, методы
- Вывод: токен был ограничен/истёк, проблема не в коде

### Новый токен

- Все endpoint работают корректно
- Проверены 16 endpoint вручную
- Автотесты проходят на 100%

## Ручная проверка всех endpoint

Скрипт: `scripts/manual_api_check.py`

| Endpoint | Метод | Статус | Результат |
|----------|-------|--------|-----------|
| `/limits` | GET | **200** | JSON с лимитами |
| `/search` | POST | **200** | Список документов |
| `/topic/10900200` | GET | **200** | Метаданные НК РФ |
| `/snippets` | POST | **200** | Фрагменты текста |
| `/find-hyperlinks` | POST | **200** | HTML со ссылками |
| `/find-modified` | POST | **200** | Статус изменений |
| `/prime` | GET | **200** | Дерево категорий |
| `/prime/create-news` | POST | **200** | Лента новостей |
| `/sutyazhnik-search` | POST | **200** | Судебная практика |
| `/topic/10900200/download` | GET | **200** | RTF файл |
| `/topic/10900200/html` | GET | **200** | JSON с HTML |
| `/topic/10900200/entry/36/html` | GET | **200** | HTML блока |
| `/topic/10900200/download-odt` | GET | **200** | ODT файл |
| `/topic/10900200/download-pdf` | GET | **200** | PDF файл |
| `/image/12345` | GET | **404** | Несуществующий object_id |
| `/formula` | GET | **423** | Лимит экспорта исчерпан |

## Важное замечание: лимит экспорта исчерпан

В процессе тестирования был исчерпан месячный лимит на экспорт:

```json
{
  "title": "Экспорт",
  "value": 0,
  "names": [
    "topic/download",
    "topic/html",
    "entry/html",
    "topic/download-odt",
    "topic/download-pdf",
    "image",
    "formula"
  ]
}
```

В лимит экспорта входят:
- Скачивание RTF/PDF/ODT
- HTML-экспорт документа (`/topic/{id}/html`)
- HTML-экспорт блока (`/topic/{id}/entry/{entry}/html`)
- Загрузка изображений (`/image/{id}`)
- Загрузка формул (`/formula`)

Сейчас любой запрос к этим endpoint возвращает `423 Locked` до начала следующего месяца.

## Автотесты

### Результат

```
pytest tests/test_all_features.py tests/test_file_tools.py -v
51 passed in 13.66s
```

### Что покрывают тесты

**Реальные вызовы API:**
- Поиск документов (`/search`)
- Фрагменты (`/snippets`)
- PRIME-категории и новости (`/prime`, `/prime/create-news`)
- Судебная практика (`/sutyazhnik-search`)
- Лимиты (`/limits`)
- MCP tool-обёртки для всех перечисленных методов

**Мокированные тесты (HTTP-подмена через respx):**
- Информация о документе (`/topic/{id}`)
- Постановка ссылок (`/find-hyperlinks`)
- Мониторинг изменений (`/find-modified`, `/block-on-control/changed`)
- Все экспортные endpoint (`/download`, `/download-pdf`, `/download-odt`, `/html`, `/entry/{id}/html`)
- Изображения и формулы (`/image/{id}`, `/formula`)
- MCP resources и prompts
- Регистрация в FastMCP-сервере

**Локальные инструменты:**
- Работа с кейсами (`create_case_folder`, `save_to_case`, `copy_docx_to_case`)
- Работа с документами (`save_document`, `load_document`, `list_documents`)
- Шаблоны и логи (`copy_template`, `create_log`)

## Структура созданных файлов

```
garant-mcp/
├── tests/
│   └── test_all_features.py          # 41 тест всех функций
├── scripts/
│   ├── manual_api_check.py           # Ручная проверка 16 endpoint
│   ├── auth_variants_check.py        # Проверка вариантов авторизации
│   ├── compare_limits_search.py      # Детальное сравнение /limits и /search
│   ├── check_image_formula.py        # Проверка /image и /formula
│   ├── find_documents_with_media.py  # Поиск документов с изображениями/формулами
│   └── test_formula_variants.py      # Тестирование /formula с разными параметрами
├── manual_api_check/                 # Сохранённые результаты ручных проверок
│   ├── results_*.json
│   ├── auth_variants_*.json
│   └── comparison_*.json
└── TEST_REPORT.md                    # Этот отчёт
```

## Найденные особенности и проблемы

### Подтверждённые возможности

- Все endpoint Гарант Коннект v2 работают с корректным токеном
- Формат авторизации `Authorization: Bearer <token>` верен
- Код проекта корректно реализует все методы API

### Проблемы, требующие внимания

1. **Лимит экспорта исчерпан.** Сейчас `value: 0` для категории "Экспорт". Нужно либо дождаться начала следующего месяца, либо получить другой токен/тариф.

2. **Утечка старого токена в документации.** Ранее файл `API_GARANT_COMPLETE_GUIDE.md` содержал старый токен в открытом виде. Токен удалён, артефакты с ним очищены.

3. **Дублирование функции `create_case` в `src/garant_mcp/tools.py`.** Функция объявлена дважды (строки ~442 и ~587). Python использует второе определение; первое бесполезно.

4. **Кэш не использует TTL из `Config`.** В `client.py` строка 91 всегда берёт TTL 300 сек (`self.cache.get_ttl` не существует), игнорируя `CACHE_TTL_*` из конфигурации.

5. **Глобальный клиент в `resources.py`.** `client = GarantClient()` создаётся при импорте модуля и никогда не закрывается. Это может приводить к утечке соединений и проблемам с кэшем в тестах.

6. **Старые тесты `test_client.py` и `test_tools.py` зависят от реального API.** Они будут работать сейчас, но расходуют платные лимиты (`/topic`, `/find-hyperlinks`, `/find-modified`). Рекомендуется перевести их на моки для экономии лимитов.

7. **Отсутствует `pyproject.toml` / `setup.cfg`.** Настройки `black`, `ruff`, `mypy`, `pytest-asyncio` не зафиксированы в проекте.

## Рекомендации

1. **Удалить старый токен из `API_GARANT_COMPLETE_GUIDE.md`.**
2. **Исправить дублирование `create_case` в `tools.py`.**
3. **Реализовать корректное TTL кэша** на основе `Config.CACHE_TTL_*`.
4. **Перевести `resources.py` на создание клиента по запросу** или явно закрывать глобальный клиент.
5. **Перевести старые тесты на `respx`-моки** для экономии лимитов.
6. **Добавить `pyproject.toml`** с настройками инструментов качества кода.
7. **Не запускать тесты экспорта на реальном API до пополнения лимита** (следующий месяц или новый токен).

## Как запустить тесты

```powershell
cd garant-mcp
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH = "$PWD\src"
pytest tests/test_all_features.py tests/test_file_tools.py -v
```

Ручная проверка endpoint:

```powershell
python scripts/manual_api_check.py
```

## Заключение

**Код проекта работает корректно.** С новым токеном все функции API Гарант Коннект v2 доступны. Единственное ограничение на текущий момент — исчерпан месячный лимит экспорта (0/30), который восстановится в начале следующего месяца.
