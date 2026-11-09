
import sys
from pathlib import Path

# Добавляем папку проекта в путь Python
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from part2 import (
    find_instructions,
    check_service_status,
    prepare_ticket,
    service_statuses
)


# Проверяем инструкции для Wi-Fi
def test_wifi_instructions():
    result = find_instructions.invoke({"topic": "wifi"})
    assert isinstance(result, str)
    assert len(result) > 0


# Проверяем инструкции для пароля
def test_password_instructions():
    result = find_instructions.invoke({"topic": "password"})
    assert isinstance(result, str)
    assert len(result) > 0


# Проверяем работающий Wi-Fi
def test_wifi_operational():
    service_statuses["wifi"] = "operational"

    result = check_service_status.invoke({
        "service": "wifi"
    })

    assert "operational" in result


# Проверяем сбой восстановления пароля
def test_password_outage():
    service_statuses["password"] = "down"

    try:
        result = check_service_status.invoke({
            "service": "password reset service"
        })

        assert result == "password service status: down"

    finally:
        service_statuses["password"] = "operational"


# Проверяем заявку без описания
def test_missing_ticket_details():
    result = prepare_ticket.invoke({
        "topic": "wifi",
        "description": ""
    })

    assert "describe" in result.lower()


# Проверяем неизвестный сервис
def test_unknown_service():
    result = check_service_status.invoke({
        "service": "unknown_service"
    })

    assert "unknown" in result
