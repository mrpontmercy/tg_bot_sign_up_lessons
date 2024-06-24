from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from services.user.kb import get_current_user_keyboard
from services.states import END, StartState
from services.templates import render_template
from services.utils import (
    add_start_over,
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_kb = await get_current_user_keyboard(update)
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
        del context.user_data["START_OVER"]
    else:
        await update.message.reply_text(
            render_template("start.jinja"), reply_markup=ReplyKeyboardRemove()
        )
        await update.message.reply_text(always_display_text, reply_markup=start_kb)
    context.user_data.clear()
    return StartState.CHOOSE_ACTION


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    context.user_data.clear()
    tg_id = update.effective_user.id
    if update.callback_query:
        await update.callback_query.answer()
        await context.bot.send_message(tg_id, "Команда завершена")
    else:
        await update.message.reply_text("Команда завершена")

    return END


@add_start_over
async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await start_command(update, context)
    return END


async def alert_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = await get_current_user_keyboard(update)
    await update.effective_message.reply_text(
        "START Сообщение не распознано. Выберите действие, либо введите /stop чтобы завершить беседу!",
        reply_markup=kb,
    )
    return StartState.CHOOSE_ACTION
