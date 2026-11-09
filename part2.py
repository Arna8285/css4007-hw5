
import json
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


# Загружаем локальные инструкции
DATA_PATH = Path(__file__).parent / "data" / "helpdesk.json"

with open(DATA_PATH, "r", encoding="utf-8") as file:
    helpdesk_data = json.load(file)


# Учебные состояния сервисов
service_statuses = {
    "wifi": "operational",
    "password": "operational"
}

MAX_STEPS = 5


@tool
def find_instructions(topic: str) -> str:
    """Find helpdesk instructions for Wi-Fi or password problems."""

    # Приводим текст к нижнему регистру
    topic = topic.lower().strip()

    # Определяем тему по ключевым словам
    if "wifi" in topic or "wi-fi" in topic:
        topic = "wifi"
    elif "password" in topic:
        topic = "password"
    else:
        return "No instructions found for this topic."

    # Получаем инструкции из JSON
    data = helpdesk_data["instructions"][topic]

    # Формируем ответ
    reply = data["title"] + "\n"
    reply += "\n".join(data["steps"])

    return reply


@tool
def check_service_status(service: str) -> str:
    """Check the simulated status of Wi-Fi or password services."""

    # Приводим название к единому формату
    service = service.lower().strip()

    # Определяем нужный сервис
    if "password" in service:
        service = "password"
    elif "wifi" in service or "wi-fi" in service:
        service = "wifi"

    # Получаем состояние сервиса
    status = service_statuses.get(service, "unknown")

    return f"{service} service status: {status}"


@tool
def prepare_ticket(topic: str, description: str) -> str:
    """Prepare a local helpdesk ticket draft."""

    # Проверяем, указана ли проблема
    if not description.strip():
        return "Please describe your problem before creating a ticket."

    # Создаём черновик обращения
    ticket = {
        "topic": topic,
        "description": description,
        "status": "draft"
    }

    # Возвращаем результат
    return (
        f"Ticket prepared successfully!\n"
        f"Topic: {ticket['topic']}\n"
        f"Description: {ticket['description']}\n"
        f"Status: {ticket['status']}"
    )


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    steps: int


def call_model(state: AgentState):

    # Получаем количество выполненных шагов
    steps = state.get("steps", 0)

    # Проверяем ограничение
    if steps >= MAX_STEPS - 1:

        # Завершаем работу без нового запроса к AI
        answer = AIMessage(
            content=(
                "The tool limit was reached. "
                "I cannot perform additional checks. "
                "Please try again with a new request. "
                "Any unverified service status is unknown."
            )
        )

    else:
        # Вызываем AI-модель
        answer = model_with_tools.invoke(state["messages"])

    return {
        "messages": [answer],
        "steps": steps + 1
    }


def route_model(state: AgentState):

    last_message = state["messages"][-1]

    # Если AI запросила инструмент, переходим к инструментам
    if last_message.tool_calls:
        return "tools"

    # Если инструментов нет, завершаем работу
    return "end"




# Создаём список инструментов
tools = [
    find_instructions,
    check_service_status,
    prepare_ticket
]


# Определяем состояние агента



# Создаём AI-модель
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

model_with_tools = model.bind_tools(tools)


# Создаём граф
def create_agent():
    builder = StateGraph(AgentState)

    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "model")

    builder.add_conditional_edges(
        "model",
        route_model,
        {
            "tools": "tools",
            "end": END
        }
    )

    builder.add_edge("tools", "model")

    return builder.compile()


if __name__ == "__main__":
    agent = create_agent()

    result = agent.invoke({
        "messages": [
            HumanMessage(
                content="I cannot connect to campus Wi-Fi. Find instructions."
            )
        ],
        "steps": 0
    })

    print(result["messages"][-1].content)
