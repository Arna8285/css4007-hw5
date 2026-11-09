
import sys
import sqlite3
from pathlib import Path

# Добавляем папку проекта в путь Python
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_core.messages import AIMessage
from part3 import create_memory_agent


# Проверяем постоянное сохранение предпочтений
def test_preference_persistence(tmp_path):

    # Создаём временную базу
    graph, store = create_memory_agent(data_dir=tmp_path)

    # Сохраняем предпочтение
    store.put(
        ("users", "student_001"),
        "language_preference",
        {"language": "simple English", "level": "A2"}
    )

    # Повторно подключаемся к базе
    new_graph, new_store = create_memory_agent(data_dir=tmp_path)

    # Проверяем восстановление
    result = new_store.get(
        ("users", "student_001"),
        "language_preference"
    )

    assert result is not None
    assert result.value["language"] == "simple English"
    assert result.value["level"] == "A2"


# Проверяем разделение пользователей
def test_user_isolation(tmp_path):

    graph, store = create_memory_agent(data_dir=tmp_path)

    # Сохраняем разные предпочтения
    store.put(
        ("users", "student_001"),
        "language_preference",
        {"language": "simple English"}
    )

    store.put(
        ("users", "student_002"),
        "language_preference",
        {"language": "Russian"}
    )

    # Получаем данные пользователей
    user_1 = store.get(
        ("users", "student_001"),
        "language_preference"
    )

    user_2 = store.get(
        ("users", "student_002"),
        "language_preference"
    )

    assert user_1.value["language"] == "simple English"
    assert user_2.value["language"] == "Russian"


# Проверяем восстановление истории диалога
def test_conversation_persistence(tmp_path):

    graph, store = create_memory_agent(data_dir=tmp_path)

    config = {
        "configurable": {
            "thread_id": "test_thread_001"
        }
    }

    # Сохраняем сообщение без вызова OpenAI API
    graph.update_state(
        config,
        {
            "messages": [
                AIMessage(content="I can help with your Wi-Fi problem.")
            ],
            "steps": 0
        },
        as_node="model"
    )

    # Создаём новый граф с той же базой
    new_graph, new_store = create_memory_agent(data_dir=tmp_path)

    # Восстанавливаем историю
    state = new_graph.get_state(config)

    messages = [
        message.content
        for message in state.values["messages"]
        if message.type == "ai"
    ]

    assert "I can help with your Wi-Fi problem." in messages
