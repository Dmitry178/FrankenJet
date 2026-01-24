import json


def extract_broker_message(message: str):
    """
    Извлечение данных из сообщения, полученного от брокера
    """

    json_data = json.loads(message)
    msg_type = json_data.get("type")
    msg_data = json_data.get("data")

    if not msg_data:
        raise ValueError("Данные отсутствуют")

    return msg_type, msg_data
