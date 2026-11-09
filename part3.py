
import sqlite3
from pathlib import Path

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore

from part2 import (
    AgentState,
    MAX_STEPS,
    tools,
    model_with_tools,
    route_model
)


# Определяем папку проекта
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


# Создаём агента с постоянной памятью
def create_memory_agent(data_dir=None):

    # Используем указанную папку или папку проекта
    if data_dir is None:
        data_dir = DATA_DIR

    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    # Подключаем базу истории диалогов
    history_connection = sqlite3.connect(
        data_dir / "agent_memory.sqlite",
        check_same_thread=False,
        isolation_level=None
    )

    checkpointer = SqliteSaver(history_connection)

    # Подключаем базу предпочтений
    store_connection = sqlite3.connect(
        data_dir / "user_preferences.sqlite",
        check_same_thread=False,
        isolation_level=None
    )

    store = SqliteStore(store_connection)
    store.setup()

    # Создаём функцию модели с памятью
    def call_model(state: AgentState, config, *, store):

        steps = state.get("steps", 0)

        # Останавливаем агента при достижении лимита
        if steps >= MAX_STEPS - 1:
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "The tool limit was reached. "
                            "I cannot perform additional checks."
                        )
                    )
                ],
                "steps": steps + 1
            }

        # Получаем предпочтения пользователя
        user_id = config["configurable"].get("user_id")
        preference = None

        if user_id:
            preference = store.get(
                ("users", user_id),
                "language_preference"
            )

        # Подготавливаем инструкции для AI
        instruction = "You are a helpful university IT assistant."

        if preference:
            language = preference.value["language"]
            level = preference.value["level"]

            instruction += (
                f" Respond in {language} at {level} level."
            )

        # Получаем ответ модели
        answer = model_with_tools.invoke(
            [
                SystemMessage(content=instruction),
                *state["messages"]
            ]
        )

        return {
            "messages": [answer],
            "steps": steps + 1
        }

    # Создаём граф
    builder = StateGraph(AgentState)

    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "model")

    builder.add_conditional_edges(
        "model",
        route_model,
        {"tools": "tools", "end": END}
    )

    builder.add_edge("tools", "model")

    # Подключаем постоянную память
    graph = builder.compile(
        checkpointer=checkpointer,
        store=store
    )

    return graph, store


if __name__ == "__main__":
    graph, store = create_memory_agent()

    print("Part 3 memory agent created successfully!")
