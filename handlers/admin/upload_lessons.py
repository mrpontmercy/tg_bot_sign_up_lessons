from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from handlers.response import send_error_message
from services.admin.upload_lessons import process_insert_lesson_into_db
from services.kb import get_back_keyboard, get_retry_or_back_keyboard
from services.states import AdminState, InterimAdminState
from services.utils import (
    add_message_info_into_context,
    delete_last_message_from_context,
)


@add_message_info_into_context
async def start_inserting_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    back_kb = get_back_keyboard(InterimAdminState.BACK_TO_ADMIN)
    await query.edit_message_text(
        "Отправьте файл с уроками установленной формы.\n",
        reply_markup=back_kb,
    )
    return AdminState.INSERT_LESSONS


async def insert_lessons_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rec_document = update.message.document
    user_tg_id = update.effective_user.id
    await delete_last_message_from_context(context)
    err, answer = await process_insert_lesson_into_db(rec_document, user_tg_id, context)
    if not err:
        retry_kb = get_retry_or_back_keyboard(
            InterimAdminState.START_UPDATE_LESSONS, InterimAdminState.BACK_TO_ADMIN
        )
        await send_error_message(user_tg_id, context, err=answer, keyboard=retry_kb)
    else:
        back_kb = get_back_keyboard(InterimAdminState.BACK_TO_ADMIN)
        await context.bot.send_message(
            user_tg_id,
            answer,
            reply_markup=back_kb,
            parse_mode=ParseMode.HTML,
        )

    return AdminState.CHOOSE_ACTION
