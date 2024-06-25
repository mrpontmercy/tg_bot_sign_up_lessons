from db import fetch_all
from services.db import execute_delete
from services.exceptions import SubscriptionError
from services.utils import Subscription, TLSubscription


async def get_available_individual_subs() -> list[Subscription]:
    r_sql = """SELECT * FROM subscription WHERE user_id IS NULL"""

    subs = await fetch_all(r_sql)
    if not subs:
        raise SubscriptionError("Не удалось найти доступные индивидуальные абонементы!")
    result = []
    for sub in subs:
        result.append(Subscription(**sub))

    return result


async def get_available_group_subs() -> list[TLSubscription]:
    r_sql = """SELECT * FROM tl_subscription WHERE user_id IS NULL"""

    subs = await fetch_all(r_sql)
    if not subs:
        raise SubscriptionError("Не удалось найти доступные групповые абонементы!")
    result = []
    for sub in subs:
        result.append(TLSubscription(**sub))

    return result


async def delete_individual_subscription(sub_id: int):
    await execute_delete("subscription", "id=:sub_id", {"sub_id": sub_id})


async def delete_group_subscription(sub_id: int):
    await execute_delete("tl_subscription", "id=:sub_id", {"sub_id": sub_id})
