import logging
import sqlite3

from telegram import Update
from telegram.ext import ContextTypes

from handlers.response import send_error_message
from services.admin.lecturer import validate_phone_number
from services.db import get_user_by_phone_number, update_user_to_lecturer
from services.decorators import admin_required
from services.exceptions import InputMessageError, UserError
from services.kb import get_back_keyboard, get_retry_or_back_keyboard
from services.states import AdminState, InterimAdminState
from services.utils import (
    add_message_info_into_context,
    delete_last_message_from_context,
)


@add_message_info_into_context
@admin_required
async def enter_lecturer_phone_number(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    back_kb = get_back_keyboard(InterimAdminState.BACK_TO_ADMIN)
    await query.edit_message_text(
        "Введите номер телефона преподователя!",
        reply_markup=back_kb,
    )
    return AdminState.ADD_LECTURER


@admin_required
async def make_lecturer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    retry_kb = get_retry_or_back_keyboard(
        InterimAdminState.ENTER_LECTURER_PHONE, InterimAdminState.BACK_TO_ADMIN
    )
    tg_id = update.effective_user.id

    await delete_last_message_from_context(context)

    try:
        phone_number = validate_phone_number(update.message.text)
        user = await get_user_by_phone_number(phone_number)
        await update_user_to_lecturer(user.id)
    except (InputMessageError, UserError) as e:
        await send_error_message(
            update.message.from_user.id, context, err=str(e), keyboard=retry_kb
        )
        return AdminState.CHOOSE_ACTION
    except sqlite3.Error as e:
        logging.getLogger(__name__).exception(e)
        await send_error_message(
            tg_id, context, err="Что-то пошло не так!", keyboard=retry_kb
        )
        return AdminState.CHOOSE_ACTION

    back_kb = get_back_keyboard(InterimAdminState.BACK_TO_ADMIN)
    await update.effective_message.reply_text(
        f"Пользователь с номером {phone_number} успешно обновлен до `Преподователь`",
        reply_markup=back_kb,
    )
    return AdminState.CHOOSE_ACTION
