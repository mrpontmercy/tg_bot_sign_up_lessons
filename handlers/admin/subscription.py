import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from config import LEN_GROUP_SUB_KEY, LEN_INDIVIDUAL_SUB_KEY
from handlers.response import (
    edit_callbackquery_template,
    send_error_message,
    send_template_message,
)
from services.kb import get_type_subscription_keyboard
from services.admin.subscription import (
    add_group_subscription_to_db,
    add_individual_subscription_to_db,
    generate_sub_key,
    validate_group_subscription_input,
    validate_num_of_classes,
)
from services.decorators import admin_required
from services.exceptions import InputMessageError
from services.kb import get_back_keyboard, get_retry_or_back_keyboard
from services.states import AdminState, InterimAdminState
from services.utils import (
    add_message_info_into_context,
    add_message_info_into_context_func,
    delete_last_message_from_context,
)


@admin_required
async def start_generating_subscription(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    type_subscription_kb = get_type_subscription_keyboard(
        InterimAdminState.BACK_TO_ADMIN
    )
    await query.edit_message_text(
        text="Выберите какого типа абонемент вы хотите сгенерировать",
        reply_markup=type_subscription_kb,
    )
    return AdminState.GENERATING_SUBSCRIPTION


@add_message_info_into_context
@admin_required
async def start_generating_individual_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    sub_key = await generate_sub_key(LEN_INDIVIDUAL_SUB_KEY)

    context.user_data["sub_key"] = sub_key
    back_kb = get_back_keyboard(InterimAdminState.BACK_TO_ADMIN)
    answer = (
        f"Отлично, теперь введите количество занятий для индивидуального абонемента!"
    )
    await query.edit_message_text(answer, reply_markup=back_kb)
    return AdminState.GENERATE_INDIVIDUAL_SUB


@admin_required
async def make_new_individual_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    retry_kb = get_retry_or_back_keyboard(
        InterimAdminState.START_GENERATE_SUB, InterimAdminState.BACK_TO_ADMIN
    )
    tg_id = update.effective_user.id
    await delete_last_message_from_context(context)

    sub_key = context.user_data["sub_key"]
    del context.user_data["sub_key"]

    try:
        num_of_classes = validate_num_of_classes(update.message.text)
        params = {
            "sub_key": sub_key,
            "num_of_classes": num_of_classes,
        }
        await add_individual_subscription_to_db(params)
    except InputMessageError as e:
        await send_error_message(
            tg_id,
            context,
            err=str(e),
            keyboard=retry_kb,
        )
        return AdminState.CHOOSE_ACTION
    except sqlite3.Error as e:
        logging.getLogger(__name__).exception(e)
        await send_error_message(
            tg_id,
            context,
            err=str(e),
            keyboard=retry_kb,
        )
        return AdminState.CHOOSE_ACTION

    res_message = await send_template_message(
        tg_id,
        "create_subscription_success.jinja",
        context=context,
        data={"sub_key": sub_key},
        keyboard=get_back_keyboard(InterimAdminState.BACK_TO_ADMIN),
    )
    # Нужно чтобы удалить текущее сообщение, а не прошлое
    add_message_info_into_context_func(
        context.user_data, update.effective_chat.id, res_message.id
    )
    return AdminState.CHOOSE_ACTION


@add_message_info_into_context
@admin_required
async def start_generating_group_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    sub_key = await generate_sub_key(LEN_GROUP_SUB_KEY)

    context.user_data["sub_key"] = sub_key
    back_kb = get_back_keyboard(InterimAdminState.BACK_TO_ADMIN)
    await edit_callbackquery_template(
        query, "generate_group_subscription.jinja", keyboard=back_kb
    )
    return AdminState.GENERATE_GROUP_SUB


@admin_required
async def make_new_group_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    retry_kb = get_retry_or_back_keyboard(
        InterimAdminState.START_GENERATE_SUB, InterimAdminState.BACK_TO_ADMIN
    )
    tg_id = update.effective_user.id
    await delete_last_message_from_context(context)

    sub_key = context.user_data["sub_key"]
    del context.user_data["sub_key"]

    try:
        n, start_date, end_date = validate_group_subscription_input(update.message.text)
        params = {
            "sub_key": sub_key,
            "num_of_classes": n,
            "start_date": start_date,
            "end_date": end_date,
        }
        await add_group_subscription_to_db(params)
    except InputMessageError as e:
        await send_error_message(
            tg_id,
            context,
            err=str(e),
            keyboard=retry_kb,
        )
        return AdminState.CHOOSE_ACTION
    except sqlite3.Error as e:
        logging.getLogger(__name__).exception(e)
        await send_error_message(
            tg_id,
            context,
            err=str(e),
            keyboard=retry_kb,
        )
        return AdminState.CHOOSE_ACTION

    res_message = await send_template_message(
        tg_id,
        "create_subscription_success.jinja",
        context=context,
        data={"sub_key": sub_key},
        keyboard=get_back_keyboard(InterimAdminState.BACK_TO_ADMIN),
    )
    return AdminState.CHOOSE_ACTION
