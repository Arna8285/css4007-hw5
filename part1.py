import json
from pathlib import Path
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

DATA_PATH = Path(__file__).parent / "data" / "helpdesk.json"

with open(DATA_PATH, "r", encoding="utf-8") as file:
    helpdesk_data = json.load(file)

class HelpdeskState(TypedDict):
    message: str
    category: str
    reply: str

def read_request(state: HelpdeskState):

    # Получаем сообщение и переводим в нижний регистр
    message = state["message"].lower()

    # Проверяем проблему с Wi-Fi
    if "wifi" in message or "wi-fi" in message:
        category = "wifi"

    # Проверяем проблему с паролем
    elif "password" in message:
        category = "password"

    # Если тема неизвестна
    else:
        category = "other"

    return {"category": category}


def read_request_v2(state: HelpdeskState):

    # Получаем сообщение
    message = state["message"].lower()

    # Проверяем наличие двух тем
    has_wifi = "wifi" in message or "wi-fi" in message
    has_password = "password" in message

    # Определяем категорию
    if has_wifi and has_password:
        category = "clarify"
    elif has_wifi:
        category = "wifi"
    elif has_password:
        category = "password"
    else:
        category = "other"

    return {"category": category}


def wifi_help(state: HelpdeskState):

    # Получаем инструкции из JSON
    data = helpdesk_data["instructions"]["wifi"]

    # Создаём ответ
    reply = data["title"] + "\n"
    reply += "\n".join(data["steps"])

    return {"reply": reply}


def password_help(state: HelpdeskState):

    # Получаем инструкции из JSON
    data = helpdesk_data["instructions"]["password"]

    # Создаём ответ
    reply = data["title"] + "\n"
    reply += "\n".join(data["steps"])

    return {"reply": reply}


def other_help(state: HelpdeskState):

    # Просим уточнить проблему
    reply = "Is your problem about Wi-Fi or a password?"

    return {"reply": reply}


def clarify_problem(state: HelpdeskState):

    # Просим выбрать проблему
    reply = "You mentioned Wi-Fi and password. Which problem should we solve first?"

    return {"reply": reply}


def choose_next(state: HelpdeskState):
    return state["category"]




# Создаём первоначальный граф
def create_original_graph():
    builder = StateGraph(HelpdeskState)

    builder.add_node("read_request", read_request)
    builder.add_node("wifi_help", wifi_help)
    builder.add_node("password_help", password_help)
    builder.add_node("other_help", other_help)

    builder.add_edge(START, "read_request")

    builder.add_conditional_edges(
        "read_request",
        choose_next,
        {
            "wifi": "wifi_help",
            "password": "password_help",
            "other": "other_help"
        }
    )

    for node in ["wifi_help", "password_help", "other_help"]:
        builder.add_edge(node, END)

    return builder.compile()


# Создаём обновлённый граф
def create_updated_graph():
    builder = StateGraph(HelpdeskState)

    builder.add_node("read_request", read_request_v2)
    builder.add_node("wifi_help", wifi_help)
    builder.add_node("password_help", password_help)
    builder.add_node("other_help", other_help)
    builder.add_node("clarify_problem", clarify_problem)

    builder.add_edge(START, "read_request")

    builder.add_conditional_edges(
        "read_request",
        choose_next,
        {
            "wifi": "wifi_help",
            "password": "password_help",
            "other": "other_help",
            "clarify": "clarify_problem"
        }
    )

    for node in ["wifi_help", "password_help", "other_help", "clarify_problem"]:
        builder.add_edge(node, END)

    return builder.compile()


# Запускаем программу
if __name__ == "__main__":

    graph = create_updated_graph()

    messages = [
        "I cannot connect to Wi-Fi.",
        "I forgot my PASSWORD.",
        "My laptop screen is broken.",
        "My Wi-Fi password does not work."
    ]

    for message in messages:
        state = {
            "message": message,
            "category": "",
            "reply": ""
        }

        result = graph.invoke(state)

        print("\nMessage:", message)
        print("Category:", result["category"])
        print("Reply:", result["reply"])
        print("-" * 50)
