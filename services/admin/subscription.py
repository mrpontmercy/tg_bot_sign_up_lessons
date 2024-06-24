import re
import string
from typing import Any, Iterable

import aiosqlite
from db import execute, fetch_all, get_db
from services.exceptions import InputMessageError, SubscriptionError


import random

from services.utils import Subscription


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


def validate_num_of_classes(message: str):
    message = message.split(" ")
    if len(message) != 1:
        raise InputMessageError("Количество слов в сообщение должно быть равным 1")

    if not re.fullmatch("\d+", message[0]):
        raise InputMessageError("Сообщение должно содержать только цифры")

    return message[0]


async def add_subscription_to_db(params: Iterable[Any]):
    try:
        await execute(
            """insert into subscription (sub_key, num_of_classes) VALUES (:sub_key, :num_of_classes)""",
            params=params,
        )
    except aiosqlite.Error as e:
        await (await get_db()).rollback()
        raise
