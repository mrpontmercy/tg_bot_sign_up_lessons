from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_STATUS, LECTURER_STATUS
from handlers.response import edit_callbackquery_template, send_error_message
from services.admin.kb import get_admin_keyboard
from services.db import get_user_by_tg_id
from services.exceptions import UserError
from services.filters import is_admin
from services.states import END, AdminState, StartState
from services.user.kb import get_current_user_keyboard


# TODO Возможно стоит совсем убрать. Пока не использовал
def ensure_no_active_conversation(func):
    @wraps(func)
    async def wrapper(update, context):
        if curr_conv := context.user_data.get("conversation"):
            text = "Сообщение не распознано. Выберите действие, либо введите /stop чтобы завершить беседу!"
            if curr_conv == "START":
                kb = await get_current_user_keyboard(update)
                await update.effective_message.reply_text(text, reply_markup=kb)
                return StartState.CHOOSE_ACTION
            elif curr_conv == "ADMIN":
                kb = get_admin_keyboard()
                await update.effective_message.reply_text(text, reply_markup=kb)
                return AdminState.CHOOSE_ACTION
        return await func(update, context)

    return wrapper


def admin_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_tg_id = update.effective_user.id
        if not is_admin(user_tg_id):
            if update.callback_query:
                await edit_callbackquery_template(
                    update.callback_query, "error.jinja", err="У вас нет доступа!"
                )
            else:
                await send_error_message(user_tg_id, context, err="У вас нет доступа!")
            return END
        return await func(update, context)

    return wrapper


def lecturer_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_tg_id = update.effective_user.id
        try:
            user = await get_user_by_tg_id(user_tg_id)
        except UserError as e:
            if update.callback_query:
                await edit_callbackquery_template(
                    update.callback_query,
                    "error.jinja",
                    err=str(e),
                )
            else:
                await send_error_message(
                    user_tg_id,
                    context,
                    err=str(e),
                )
            return END

        if user.status != LECTURER_STATUS:
            if update.callback_query:
                await edit_callbackquery_template(
                    update.callback_query,
                    "error.jinja",
                    err="У вас нет доступа!",
                )
            else:
                await send_error_message(
                    user_tg_id,
                    context,
                    err="У вас нет доступа!",
                )
            return END

        return await func(update, context)

    return wrapper


def define_user_status(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_tg_id = update.effective_user.id
        user_is_admin = is_admin(user_tg_id)
        if user_is_admin:
            context.user_data["user_status"] = ADMIN_STATUS
        else:
            try:
                user = await get_user_by_tg_id(user_tg_id)
            except UserError as e:
                if update.callback_query:
                    await edit_callbackquery_template(
                        update.callback_query,
                        "error.jinja",
                        err=str(e),
                    )
                else:
                    await send_error_message(
                        user_tg_id,
                        context,
                        err=str(e),
                    )
                return END
            if user.status == LECTURER_STATUS:
                context.user_data["user_status"] = LECTURER_STATUS
        return await func(update, context)

    return wrapper
