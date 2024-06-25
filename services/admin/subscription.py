import re
import string
from typing import Any, Iterable

import aiosqlite
from db import execute, fetch_all, get_db
from services.exceptions import InputMessageError, SubscriptionError


import random

from services.utils import DATE_PATTERN, Subscription


unity = string.ascii_letters + string.digits


async def get_all_subs():
    r_sql = """SELECT * FROM subscription"""

    subs = await fetch_all(r_sql)
    if not subs:
        raise SubscriptionError("Не удалось найти ни одного абонемента!")

    result = []
    for sub in subs:
        result.append(Subscription(**sub))

    return result


async def generate_sub_key(k: int):
    try:
        subs = await get_all_subs()
    except SubscriptionError as e:
        subs = []
        pass

    while True:
        sub_key = "".join(random.choices(unity, k=k))
        if not any([True if sub_key == el.sub_key else False for el in subs]):
            break

    return sub_key


def validate_group_subscription_input(message: str):
    lst_message = message.split("\n")
    if len(lst_message) != 3:
        raise InputMessageError(
            "Нужно ввести количество мест, дату начала и дату окончания абонемента через пробелы"
        )
    n, s, f = lst_message
    try:
        num_of_seats = validate_num_of_classes(n.strip())
    except InputMessageError:
        raise

    if not re.fullmatch(DATE_PATTERN, s.strip()):
        raise InputMessageError("Неверно введена дата начала абонемента!")

    if not re.fullmatch(DATE_PATTERN, f.strip()):
        raise InputMessageError("Неверно введена дата окончания абонемента!")

    return lst_message


def validate_num_of_classes(message: str):
    message = message.split(" ")
    if len(message) != 1:
        raise InputMessageError("Количество слов в сообщение должно быть равным 1")

    if not re.fullmatch("\d+", message[0]):
        raise InputMessageError("Сообщение должно содержать только цифры")

    return message[0]


async def add_individual_subscription_to_db(params: Iterable[Any]):
    try:
        await execute(
            """insert into subscription (sub_key, num_of_classes) VALUES (:sub_key, :num_of_classes)""",
            params=params,
        )
    except aiosqlite.Error as e:
        await (await get_db()).rollback()
        raise


async def add_group_subscription_to_db(params: Iterable[Any]):
    try:
        await execute(
            """insert into tl_subscription (sub_key, num_of_classes, start_date, end_date) VALUES (:sub_key, :num_of_classes, :start_date, :end_date)""",
            params=params,
        )
    except aiosqlite.Error as e:
        await (await get_db()).rollback()
        raise
