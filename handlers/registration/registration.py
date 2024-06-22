import logging
import sqlite3
from telegram import Update, User
from telegram.ext import ContextTypes

from handlers.response import edit_callbackquery_template, send_template_message
from handlers.start import get_current_keyboard
from services.exceptions import ValidationError
from services.kb import get_back_kb, get_retry_or_back_keyboard
from services.registration.registration import insert_user, validate_message
from services.states import END, InterimStartState, StartState
from services.utils import (
    add_message_info_into_context,
    add_start_over,
    delete_last_message_from_context,
)


@add_message_info_into_context
@add_start_over
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    back_kb = get_back_kb(InterimStartState.BACK_TO_START)
    await edit_callbackquery_template(query, "registration.jinja", keyboard=back_kb)
    return StartState.REGISTRATION


@add_start_over
async def user_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await delete_last_message_from_context(context)
    user = update.effective_user
    full_info = [user.id, user.username] + update.effective_message.text.split(" ")
    retry_kb = get_retry_or_back_keyboard(InterimStartState.START_REGISTER, END)
    back_kb = get_back_kb(InterimStartState.BACK_TO_START)
    try:
        validated_message: User = validate_message(full_info)
    except ValidationError as e:
        await update.effective_message.reply_text(
            "Ошибка в данных, попробуйте снова. Возможная ошибка:\n\n" + str(e),
            reply_markup=retry_kb,
        )
        return StartState.SHOWING

    params = validated_message.to_dict()
    try:
        await insert_user(params)
    except sqlite3.Error as e:
        logging.getLogger(__name__).exception(e)
        await context.bot.send_message(
            user.id,
            "Произошла ошибка.\nНачните регистрацию заново",
            reply_markup=back_kb,
        )
        return StartState.SHOWING
    kb = await get_current_keyboard(update)
    await update.effective_message.reply_text(
        "Вы успешно зарегестрировались!", reply_markup=back_kb
    )
    return StartState.SHOWING
