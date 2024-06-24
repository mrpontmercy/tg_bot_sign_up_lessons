from sqlite3 import Error
from db import get_db
from services.db import execute_delete, execute_update, fetch_one_subscription_where_cond
from services.exceptions import InputMessageError, InvalidSubKey, SubscriptionError
from services.utils import Subscription, UserID


def validate_args(args: list[str] | None):
    if args is not None and len(args) != 1:
        raise InputMessageError(
            "Нужно ввести только ключ абонемента!.\nПопробуйте снова."
        )

    return args


async def activate_key(sub_key: str, user: UserID):
    try:
        curr_key_sub = await _get_sub_from_key(sub_key)
    except InvalidSubKey:
        raise

    sub_by_user = await fetch_one_subscription_where_cond(
        "user_id=:user_id", {"user_id": user.id}
    )
    if sub_by_user is not None:
        num_of_classes_left = sub_by_user.num_of_classes
        result_num_of_classes = num_of_classes_left + curr_key_sub.num_of_classes
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
                    "sub_key": curr_key_sub.sub_key,
                },
                autocommit=False,
            )
        except Error as e:
            await (await get_db()).rollback()
            raise
        await (await get_db()).commit()
        return "Ваш абонемент обновлен"
    try:
        await execute_update(
            "subscription",
            "user_id=:user_id, num_of_classes=:num_of_classes",
            "sub_key=:sub_key",
            {
                "num_of_classes": curr_key_sub.num_of_classes,
                "user_id": user.id,
                "sub_key": curr_key_sub.sub_key,
            },
        )
    except Error as e:
        raise
    return "Ваш абонемент активирован"


async def _get_sub_from_key(sub_key: str):
    curr_key_sub: Subscription | None = await fetch_one_subscription_where_cond(
        "sub_key=:sub_key",
        {"sub_key": sub_key},
    )
    if curr_key_sub is None:
        raise InvalidSubKey("Данный ключ невалиден. Обратитесь за другим ключом.")
    elif curr_key_sub.user_id is not None:
        raise InvalidSubKey(
            "Данный ключ уже зарегестрирован.\nОбратитесь за другим ключом."
        )

    return curr_key_sub


async def get_user_subscription(user_db_id: int):
    subsciption_by_user = await fetch_one_subscription_where_cond(
        "user_id=:user_id",
        {"user_id": user_db_id},
    )
    if subsciption_by_user is None:
        raise SubscriptionError("У пользователя нет абонемент")
    elif subsciption_by_user.num_of_classes == 0:
        raise SubscriptionError(
            "В вашем абонементе не осталось занятий. Обратитесь за новым абонемент!"
        )

    return subsciption_by_user
