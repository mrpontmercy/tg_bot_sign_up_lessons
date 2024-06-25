from datetime import datetime
from sqlite3 import Error
from config import (
    LEN_GROUP_SUB_KEY,
    LEN_INDIVIDUAL_SUB_KEY,
    SUB_GROUP_CODE,
    SUB_INDIVIDUAL_CODE,
)
from db import get_db
from services.db import (
    execute_delete,
    execute_update,
    fetch_one_group_subscription_where_cond,
    fetch_one_subscription_where_cond,
)
from services.exceptions import InputMessageError, InvalidSubKey, SubscriptionError
from services.utils import Subscription, TLSubscription, UserID


def validate_args(args: list[str] | None):
    if args is not None and len(args) != 1:
        raise InputMessageError(
            "Нужно ввести только ключ абонемента!.\nПопробуйте снова."
        )

    return args


async def get_user_subscription_by_key_length(user_id, sub_key_len: int):
    if sub_key_len == LEN_INDIVIDUAL_SUB_KEY:
        sub_user = await fetch_one_subscription_where_cond(
            "user_id=:user_id", {"user_id": user_id}
        )
    elif sub_key_len == LEN_GROUP_SUB_KEY:
        sub_user = await fetch_one_group_subscription_where_cond(
            "user_id=:user_id", {"user_id": user_id}
        )
    else:
        sub_user = None
    return sub_user


async def activate_subscription_by_key(sub_key: str, user: UserID):
    try:
        curr_sub_by_key = await _get_sub_from_key(sub_key)
    except InvalidSubKey:
        raise

    sub_by_user = await get_user_subscription_by_key_length(
        user.id, len(curr_sub_by_key.sub_key)
    )
    # Если это индивидуальная подписка то просто увеличиваем количество занятий на абонементе
    if sub_by_user is not None and len(sub_by_user.sub_key) == LEN_INDIVIDUAL_SUB_KEY:
        num_of_classes_left = sub_by_user.num_of_classes
        result_num_of_classes = num_of_classes_left + curr_sub_by_key.num_of_classes
        try:
            await execute_delete(
                "subscription",
                "user_id=:user_id",
                {"user_id": user.id},
                autocommit=False,
            )
            await execute_update(
                "subscription",
                "user_id=:user_id, num_of_classes=:num_of_classes",
                "sub_key=:sub_key",
                {
                    "num_of_classes": result_num_of_classes,
                    "user_id": user.id,
                    "sub_key": curr_sub_by_key.sub_key,
                },
                autocommit=False,
            )
        except Error as e:
            await (await get_db()).rollback()
            raise
        await (await get_db()).commit()
        return "Ваш индивидаульный абонемент обновлен"

    if sub_by_user is not None:
        if (sub_by_user.num_of_classes > 0) and (
            datetime.date(datetime.strptime(sub_by_user.end_date, "%Y-%m-%d"))
            >= datetime.date(datetime.now())
        ):
            return "У вас уже есть групповой абонемент. Дождитесь его окончания и обратитесь за новым ключом для продления."

    try:
        sub_type = ""
        if len(curr_sub_by_key.sub_key) == LEN_INDIVIDUAL_SUB_KEY:
            await execute_update(
                "subscription",
                "user_id=:user_id, num_of_classes=:num_of_classes",
                "sub_key=:sub_key",
                {
                    "num_of_classes": curr_sub_by_key.num_of_classes,
                    "user_id": user.id,
                    "sub_key": curr_sub_by_key.sub_key,
                },
            )
            sub_type = "индивидуальный"
        elif len(curr_sub_by_key.sub_key) == LEN_GROUP_SUB_KEY:
            await execute_update(
                "tl_subscription",
                "user_id=:user_id, num_of_classes=:num_of_classes, start_date=:start_date, end_date=:end_date",
                "sub_key=:sub_key",
                {
                    "num_of_classes": curr_sub_by_key.num_of_classes,
                    "user_id": user.id,
                    "sub_key": curr_sub_by_key.sub_key,
                    "start_date": curr_sub_by_key.start_date,
                    "end_date": curr_sub_by_key.end_date,
                },
            )
            sub_type = "групповой"
        return f"Ваш {sub_type} абонемент активирован"
    except Error:
        await (await get_db()).rollback()
        raise


async def _get_sub_from_key(sub_key: str) -> TLSubscription | Subscription:
    if len(sub_key) == LEN_INDIVIDUAL_SUB_KEY:
        curr_key_sub: Subscription | None = await fetch_one_subscription_where_cond(
            "sub_key=:sub_key",
            {"sub_key": sub_key},
        )
    elif len(sub_key) == LEN_GROUP_SUB_KEY:
        curr_key_sub: TLSubscription | None = (
            await fetch_one_group_subscription_where_cond(
                "sub_key=:sub_key",
                {"sub_key": sub_key},
            )
        )
    else:
        curr_key_sub = None

    if curr_key_sub is None:
        raise InvalidSubKey("Данный ключ невалиден. Обратитесь за другим ключом.")
    elif curr_key_sub.user_id is not None:
        raise InvalidSubKey(
            "Данный ключ уже зарегестрирован.\nОбратитесь за другим ключом."
        )

    return curr_key_sub


async def get_user_subscription(user_db_id: int, subscription_type: int):
    if subscription_type == SUB_INDIVIDUAL_CODE:
        subsciption_by_user = await fetch_one_subscription_where_cond(
            "user_id=:user_id",
            {"user_id": user_db_id},
        )
    elif subscription_type == SUB_GROUP_CODE:
        subsciption_by_user = await fetch_one_group_subscription_where_cond(
            "user_id=:user_id",
            {"user_id": user_db_id},
        )
    else:
        subsciption_by_user = None

    if subsciption_by_user is None:
        raise SubscriptionError("У пользователя нет абонемент")
    elif subsciption_by_user.num_of_classes == 0:
        raise SubscriptionError(
            "В вашем абонементе не осталось занятий. Обратитесь за новым абонемент!"
        )

    return subsciption_by_user
