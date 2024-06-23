import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from handlers.response import send_error_message, send_template_message
from services.admin.subscription import (
    add_subscription_to_db,
    generate_sub_key,
    validate_num_of_classes,
)
from services.exceptions import InputMessageError
from services.kb import get_back_keyboard, get_retry_or_back_keyboard
from services.states import AdminState, InterimAdminState
from services.utils import (
    add_message_info_into_context,
    add_message_info_into_context_func,
    delete_last_message_from_context,
)


@add_message_info_into_context
async def start_generating_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    sub_key = await generate_sub_key(20)

    context.user_data["sub_key"] = sub_key
    back_kb = get_back_keyboard(InterimAdminState.BACK_TO_ADMIN)
    answer = f"Отлично, теперь введите количество уроков для подписки!"
    await query.edit_message_text(answer, reply_markup=back_kb)
    return AdminState.GENERATE_SUB


async def make_new_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await add_subscription_to_db(params)
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
