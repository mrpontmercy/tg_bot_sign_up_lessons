import sqlite3
from telegram import Update
from telegram.ext import ContextTypes

from config import CALLBACK_SUB_PREFIX
from handlers.response import edit_callbackquery_template
from services.admin.list_subscription import delete_subscription, get_available_subs
from services.exceptions import SubscriptionError
from services.kb import get_back_keyboard, get_flip_delete_back_keyboard
from services.states import InterimAdminState, SwitchState
from services.utils import Subscription


async def list_available_subs_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    back_kb = get_back_keyboard(SwitchState.RETURN_PREV_CONV)
    try:
        subs: list[Subscription] = await get_available_subs()
    except SubscriptionError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION

    switch_kb = get_flip_delete_back_keyboard(
        0, len(subs), CALLBACK_SUB_PREFIX, str(SwitchState.RETURN_PREV_CONV)
    )
    sub = subs[0]
    context.user_data["sub_id"] = sub.id

    await edit_callbackquery_template(
        query,
        "subs.jinja",
        data={"sub_key": sub.sub_key, "num_of_classes": sub.num_of_classes},
        keyboard=switch_kb,
    )
    return SwitchState.CHOOSE_ACTION


async def list_subs_button_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    back_kb = get_back_keyboard(SwitchState.RETURN_PREV_CONV)
    try:
        subs = await get_available_subs()
    except SubscriptionError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION
    current_index = int(query.data[len(CALLBACK_SUB_PREFIX) :])
    sub = subs[current_index]
    context.user_data["sub_id"] = sub.id

    switch_kb = get_flip_delete_back_keyboard(
        current_index, len(subs), CALLBACK_SUB_PREFIX, str(SwitchState.RETURN_PREV_CONV)
    )
    await edit_callbackquery_template(
        query,
        "subs.jinja",
        data={"sub_key": sub.sub_key, "num_of_classes": sub.num_of_classes},
        keyboard=switch_kb,
    )
    return SwitchState.CHOOSE_ACTION


async def remove_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sub_id: int | None = context.user_data.get("sub_id")
    back_kb = get_back_keyboard(SwitchState.RETURN_PREV_CONV)
    if sub_id is None:
        await edit_callbackquery_template(
            query, "error.jinja", err="Не удалось найти подписку!", keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION

    try:
        await delete_subscription(sub_id)
    except sqlite3.Error:
        await edit_callbackquery_template(
            query,
            "error.jinja",
            err="Не удалось удалить подписку! Обратитесь к администратору",
            keyboard=back_kb,
        )
        return SwitchState.CHOOSE_ACTION

    back_kb = get_back_keyboard(InterimAdminState.LIST_AVAILABLE_SUBS)
    await query.edit_message_text("Абонемент удален!", reply_markup=back_kb)
    return SwitchState.CHOOSE_ACTION
