from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
)

from handlers.response import send_error_message
from services.admin.upload_lessons import process_insert_lesson_into_db
from services.kb import (
    get_back_keyboard,
    get_type_lesson_keyboard,
)
from services.states import END, UploadLessonsState
from services.utils import (
    add_message_info_into_context,
    delete_last_message_from_context,
)


@add_message_info_into_context
async def start_inserting_lessons(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choose_type_lesson_kb = get_type_lesson_keyboard(UploadLessonsState.RETURN_PREV_CONV)
    await query.edit_message_text(
        "Выберите какого типа уроки хотите добавить\n",
        reply_markup=choose_type_lesson_kb,
    )
    return UploadLessonsState.UPDATING_LESSONS


@add_message_info_into_context
async def start_inserting_group_lessons(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    back_kb = get_back_keyboard(UploadLessonsState.RETURN_BACK)
    await query.edit_message_text(
        "Отправьте файл с групповыми уроками установленной формы.\n",
        reply_markup=back_kb,
    )
    return UploadLessonsState.INSERT_GROUP_LESSONS


@add_message_info_into_context
async def start_inserting_individual_lessons(
    update: Update, _: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    back_kb = get_back_keyboard(UploadLessonsState.RETURN_BACK)
    await query.edit_message_text(
        "Отправьте файл с индивидуальными уроками установленной формы.\n",
        reply_markup=back_kb,
    )
    return UploadLessonsState.INSERT_INDIVIDUAL_LESSONS


async def insert_group_lessons_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    rec_document = update.message.document
    user_tg_id = update.effective_user.id
    await delete_last_message_from_context(context)
    err, answer = await process_insert_lesson_into_db(
        rec_document, user_tg_id, is_group=True, context=context
    )
    if not err:
        back_kb = get_back_keyboard(UploadLessonsState.RETURN_BACK)
        await send_error_message(user_tg_id, context, err=answer, keyboard=back_kb)
    else:
        back_kb = get_back_keyboard(UploadLessonsState.RETURN_BACK)
        await context.bot.send_message(
            user_tg_id,
            answer,
            reply_markup=back_kb,
            parse_mode=ParseMode.HTML,
        )

    return UploadLessonsState.UPDATING_LESSONS


async def insert_individual_lessons_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    rec_document = update.message.document
    user_tg_id = update.effective_user.id
    await delete_last_message_from_context(context)
    err, answer = await process_insert_lesson_into_db(
        rec_document, user_tg_id, is_group=False, context=context
    )
    if not err:
        back_kb = get_back_keyboard(UploadLessonsState.RETURN_BACK)
        await send_error_message(user_tg_id, context, err=answer, keyboard=back_kb)
    else:
        back_kb = get_back_keyboard(UploadLessonsState.RETURN_BACK)
        await context.bot.send_message(
            user_tg_id,
            answer,
            reply_markup=back_kb,
            parse_mode=ParseMode.HTML,
        )

    return UploadLessonsState.UPDATING_LESSONS


async def stop_updating_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Добавление занятий завершено!"
    query = update.callback_query
    if query:
        await query.answer()

        await query.edit_message_text(text)
    else:
        await update.effective_message.reply_text(text)

    return UploadLessonsState.RETURN_PREV_CONV
