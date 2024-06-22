from telegram import Update
from telegram.ext import ContextTypes

from services.db import get_user_by_tg_id
from services.exceptions import UserError
from services.kb import get_non_register_keyboard, get_registred_keyboard
from services.states import END, StartState
from services.templates import render_template
from services.utils import add_start_over


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_kb = await get_current_keyboard(update)
    always_display_text = render_template("start_choose_action.jinja")
    # если к функции обращаются повторно, не отображается приветственное сообщение
    if context.user_data.get("START_OVER"):
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                always_display_text, reply_markup=start_kb
            )
        else:
            await context.bot.send_message(
                update.effective_user.id, always_display_text, reply_markup=start_kb
            )
    else:
        await update.message.reply_text(
            render_template("start.jinja") + always_display_text, reply_markup=start_kb
        )
    context.user_data.clear()
    return StartState.CHOOSE_ACTION


async def get_current_keyboard(update: Update):
    """
    Получение клавиатуры, которая соответствует данному пользователю
    """
    user_tg_id = update.effective_user.id
    kb = None
    try:
        await get_user_by_tg_id(user_tg_id)
    except UserError as e:
        kb = get_non_register_keyboard()
    else:
        kb = get_registred_keyboard()

    return kb


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    await update.message.reply_text("Все завершено!")

    return END


@add_start_over
async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await start_command(update, context)
    return END
