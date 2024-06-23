from db import fetch_all
from services.db import execute_delete
from services.exceptions import SubscriptionError
from services.utils import Subscription


async def get_available_subs() -> list[Subscription]:
    r_sql = """SELECT * FROM subscription WHERE user_id IS NULL"""

    subs = await fetch_all(r_sql)
    if not subs:
        raise SubscriptionError("Не удалось найти доступные абонементы!")
    result = []
    for sub in subs:
        result.append(Subscription(**sub))

    return result


async def delete_subscription(sub_id: int):
    await execute_delete("subscription", "id=:sub_id", {"sub_id": sub_id})
