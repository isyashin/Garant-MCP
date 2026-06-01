"""Example workflow script for Agent Garant - Lawyer.

Usage:
    python workflow_example.py
"""

import asyncio
import json
from pathlib import Path

# Import MCP tools
from garant_mcp.tools import (
    search_documents,
    search_judicial_practice,
    create_legal_document,
    save_text_document,
    load_text_document,
    create_case,
)


async def research_topic(topic: str) -> dict:
    """Research a legal topic.
    
    Args:
        topic: Search query.
    
    Returns:
        Dictionary with laws and practice.
    """
    print(f"🔍 Исследуем тему: {topic}")
    
    # Search legislation
    laws = await search_documents(topic)
    print(f"   Найдено законов: {len(laws.get('documents', []))}")
    
    # Search judicial practice
    practice = await search_judicial_practice(topic)
    print(f"   Найдено решений: {len(practice.get('documents', []))}")
    
    return {
        "laws": laws,
        "practice": practice,
    }


async def prepare_case(case_name: str, topic: str) -> str:
    """Prepare a new legal case.
    
    Args:
        case_name: Name of the case.
        topic: Legal topic to research.
    
    Returns:
        Path to case folder.
    """
    print(f"📁 Создаем кейс: {case_name}")
    
    # Create case folder
    case_path = await create_case(case_name)
    
    # Research topic
    research = await research_topic(topic)
    
    # Save results
    await save_text_document(
        json.dumps(research["laws"], ensure_ascii=False, indent=2),
        "законодательство.json",
        "documents"
    )
    
    await save_text_document(
        json.dumps(research["practice"], ensure_ascii=False, indent=2),
        "судебная_практика.json",
        "practice"
    )
    
    print(f"✅ Кейс создан: {case_path}")
    return case_path


async def main():
    """Main workflow example."""
    print("=" * 60)
    print("Агент Гарант - Юрист")
    print("Пример workflow")
    print("=" * 60)
    
    # Example: Car return case
    case_name = "Возврат_автомобиля"
    topic = "защита прав потребителей автомобиль гарантийный ремонт"
    
    # Prepare case
    case_path = await prepare_case(case_name, topic)
    
    print("\n📋 Следующие шаги:")
    print("1. Задайте уточняющие вопросы пользователю")
    print("2. Подготовьте документы на основе исследования")
    print("3. Проверьте документы перед отправкой")
    
    print(f"\n📂 Результаты сохранены в: {case_path}")


if __name__ == "__main__":
    asyncio.run(main())
