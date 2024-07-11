from telegram import Update
from telegram.ext import ContextTypes

from handlers.response import edit_callbackquery_template, send_template_message
from services.lecturer.kb import get_lecturer_keyboard
from services.states import LecturerState, StopState


async def lecturer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id

    kb = get_lecturer_keyboard()

    if update.callback_query:
        await update.callback_query.answer()
        await edit_callbackquery_template(
            update.callback_query, "lecturer.jinja", keyboard=kb
        )
    else:
        await send_template_message(
            tg_id, context=context, template_name="lecturer.jinja", keyboard=kb
        )

    context.user_data.clear()
    return LecturerState.CHOOSE_ACTION


async def return_to_lecturer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершить текущую беседу и вернуться к lecturer"""
    if update.callback_query:
        await update.callback_query.answer()
    # await delete_last_message_from_context(context)
    await lecturer_command(update, context)
    return StopState.STOPPING


async def alert_user_lecturer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = get_lecturer_keyboard()
    await update.effective_message.reply_text(
        "Сообщение не распознано. Выберите действие, либо введите /stop чтобы завершить беседу!",
        reply_markup=kb,
    )
    return LecturerState.CHOOSE_ACTION
