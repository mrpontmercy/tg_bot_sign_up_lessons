from telegram import Update
from telegram.ext import ContextTypes

from handlers.response import (
    edit_callbackquery_template,
    send_template_message,
)
from services.user.kb import get_current_user_keyboard
from services.admin.kb import get_admin_keyboard
from services.states import END, AdminState
from services.decorators import (
    ensure_no_active_conversation,
)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id

    kb = get_admin_keyboard()
    if update.callback_query:
        await update.callback_query.answer()
        await edit_callbackquery_template(
            update.callback_query, "admin.jinja", keyboard=kb
        )
    else:
        await send_template_message(
            tg_id, context=context, template_name="admin.jinja", keyboard=kb
        )
    context.user_data.clear()
    return AdminState.CHOOSE_ACTION


async def return_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершить текущую беседу и вернуться к admin"""
    if update.callback_query:
        await update.callback_query.answer()
    # await delete_last_message_from_context(context)
    await admin_command(update, context)
    return END


async def alert_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = await get_current_user_keyboard(update)
    await update.effective_message.reply_text(
        "Сообщение не распознано. Выберите действие, либо введите /stop чтобы завершить беседу!",
        reply_markup=kb,
    )
    return AdminState.CHOOSE_ACTION
