import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from config import SUB_GROUP_CODE, SUB_INDIVIDUAL_CODE
from handlers.response import edit_callbackquery_template, send_error_message
from services.db import get_user_by_tg_id
from services.exceptions import (
    InputMessageError,
    InvalidSubKey,
    SubscriptionError,
    UserError,
)
from services.kb import (
    get_back_keyboard,
    get_retry_or_back_keyboard,
    get_type_subscription_keyboard,
)
from services.states import END, InterimStartState, StartState
from services.user.subscription import (
    activate_subscription_by_key,
    get_user_subscription,
    validate_args,
)
from services.utils import (
    add_message_info_into_context,
    add_start_over,
    delete_last_message_from_context,
)


@add_message_info_into_context
@add_start_over
async def start_activating_subkey(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()
    kb = get_back_keyboard(InterimStartState.BACK_TO_START)
    try:
        user = await get_user_by_tg_id(update.effective_user.id)
    except UserError as e:
        await edit_callbackquery_template(
            query=query, template_name="error.jinja", err=str(e), keyboard=kb
        )
        return StartState.SHOWING

    await query.edit_message_text("Отправьте ключ абонемента!", reply_markup=kb)
    context.user_data["curr_user_tg_id"] = user.telegram_id
    return StartState.ACTIVATE_SUBSCRIPTION


async def register_sub_key_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mess_args = update.message.text.split(" ")
    retry_kb = get_retry_or_back_keyboard(
        InterimStartState.START_ACTIVATE_SUBSCRIPTION, InterimStartState.BACK_TO_START
    )
    await delete_last_message_from_context(context)
    user_tg_id = context.user_data.get("curr_user_tg_id")

    if user_tg_id is None:
        await send_error_message(user_tg_id, context, err=str(e), keyboard=retry_kb)
        return StartState.CHOOSE_ACTION
    try:
        args = validate_args(mess_args)
    except InputMessageError as e:
        await send_error_message(user_tg_id, context, err=str(e), keyboard=retry_kb)
        return StartState.CHOOSE_ACTION

    sub_key = args[0]
    try:
        user = await get_user_by_tg_id(user_tg_id)
        final_message = await activate_subscription_by_key(sub_key, user)
    except (InvalidSubKey, UserError) as e:
        await send_error_message(user_tg_id, context, err=str(e), keyboard=retry_kb)
        return StartState.CHOOSE_ACTION
    except sqlite3.Error as e:
        logging.getLogger(__name__).exception(e)
        await send_error_message(
            user_tg_id,
            context,
            err="Не удалось выполнить операцию.",
            keyboard=retry_kb,
        )
        return StartState.CHOOSE_ACTION

    back_kb = get_back_keyboard(InterimStartState.BACK_TO_START)
    await update.effective_message.reply_text(final_message, reply_markup=back_kb)
    return StartState.CHOOSE_ACTION


@add_start_over
async def show_remainder_of_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    back_kb = get_back_keyboard(InterimStartState.BACK_TO_START)
    query = update.callback_query
    await query.answer()

    type_subs_kb = get_type_subscription_keyboard(InterimStartState.BACK_TO_START)
    await query.edit_message_text(
        text="Выберите остаток какой подписки вы хотите посмотреть",
        reply_markup=type_subs_kb,
    )

    return StartState.CHOOSE_SUBSCRIPTION


async def show_remainder_of_individual_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    back_kb = get_back_keyboard(InterimStartState.SHOW_REMAINDER_SUBSCRIPTION)
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id
    user = await get_user_by_tg_id(tg_id)
    try:
        subscription = await get_user_subscription(
            user_db_id=user.id, subscription_type=SUB_INDIVIDUAL_CODE
        )
    except SubscriptionError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return StartState.CHOOSE_ACTION

    await query.edit_message_text(
        f"У вас осталось {subscription.num_of_classes} занятий на индивидуальном абонементе",
        reply_markup=back_kb,
    )
    return StartState.CHOOSE_ACTION


async def show_remainder_of_group_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    back_kb = get_back_keyboard(InterimStartState.SHOW_REMAINDER_SUBSCRIPTION)
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id
    user = await get_user_by_tg_id(tg_id)
    try:
        subscription = await get_user_subscription(
            user_db_id=user.id, subscription_type=SUB_GROUP_CODE
        )
    except SubscriptionError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return StartState.CHOOSE_ACTION

    data = {
        "start_date": subscription.start_date,
        "end_date": subscription.end_date,
        "num_of_classes": subscription.num_of_classes,
    }
    await edit_callbackquery_template(
        query,
        "group_subscription_info.jinja",
        data=data,
        keyboard=back_kb,
    )
    return StartState.CHOOSE_ACTION
