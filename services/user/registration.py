import re
from typing import Any, Iterable

from services.db import execute_insert
from services.exceptions import (
    ValidationEmailError,
    ValidationFirstNameError,
    ValidationPhoneNumberError,
    ValidationSecondNameError,
    ValidationUserError,
)
from services.utils import EMAIL_PATTERN, FS_NAME_PATTERN, PHONE_NUMBER_PATTERN, User


def validate_message(input_message: list[str]):
    # обработать строку пользователя
    try:
        validated_message = _validate_user(input_message)
    except (
        ValidationFirstNameError,
        ValidationSecondNameError,
        ValidationUserError,
        ValidationPhoneNumberError,
        ValidationEmailError,
    ):
        raise
    return validated_message


def _validate_user(user_info: list[str]) -> User:
    if len(user_info) != 6:
        raise ValidationUserError("Введены не все регестрационные данные данные")

    f_name = user_info[2]
    if not re.fullmatch(FS_NAME_PATTERN, f_name):
        raise ValidationFirstNameError("`Имя должно` содержать только буквы!")

    s_name = user_info[3]
    if not re.fullmatch(FS_NAME_PATTERN, s_name):
        raise ValidationSecondNameError("`Фамилия` должно содержать только буквы!")

    phone_number = user_info[4]
    if not re.fullmatch(PHONE_NUMBER_PATTERN, phone_number):
        raise ValidationPhoneNumberError("Неверный номер пользователя")

    email = user_info[5]
    if not re.fullmatch(EMAIL_PATTERN, email):
        raise ValidationEmailError("Неверный Email!")

    return User(*user_info)


async def insert_user(params: Iterable[Any]):
    table = "user"
    columns = "telegram_id, username, f_name, s_name, phone_number, email"
    values = ":telegram_id, :username, :f_name, :s_name, :phone_number, :email"
    await execute_insert(table, columns, values, params)
