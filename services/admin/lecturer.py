import re

from services.exceptions import InputMessageError
from services.utils import PHONE_NUMBER_PATTERN


def validate_phone_number(message: str):
    message = message.split(" ")
    if len(message) != 1:
        raise InputMessageError("Количество слов в сообщение должно быть равным 1")

    if not re.fullmatch(PHONE_NUMBER_PATTERN, message[0]):
        raise InputMessageError(
            "Сообщение должно содержать номер телефона. Начинается с 8. Всего 11 цифр"
        )

    return message[0]
