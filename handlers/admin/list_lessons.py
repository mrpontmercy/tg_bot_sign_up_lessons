from sqlite3 import Error
from telegram import Update
from telegram.ext import ContextTypes

from config import CALLBACK_LESSON_PREFIX
from handlers.response import edit_callbackquery_template
from services.admin.list_lessons import (
    process_delete_lesson_admin,
    process_delete_lesson_db,
)
from services.db import get_user_by_id, get_user_by_tg_id
from services.decorators import admin_required
from services.exceptions import LessonError, UserError
from services.kb import get_back_keyboard, get_flip_edit_delete_back_keyboard
from services.lesson import lessons_button, get_all_lessons_from_db
from services.states import END, InterimAdminState, StopState, SwitchState
from services.user.lesson import get_lessons


@admin_required
async def show_all_lessons_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получить список всех доступных уроков, на которые пользователь еще не записан! (сортировать по дате начала занятия)
    Отобразить первый урок, добавить клавиатуру
    """

    query = update.callback_query
    await query.answer()

    user_tg_id = update.effective_user.id

    context.user_data["curr_user_tg_id"] = user_tg_id

    back_kb = get_back_keyboard(SwitchState.RETURN_PREV_CONV)
    try:
        lessons = await get_all_lessons_from_db()
    except LessonError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION

    context.user_data["curr_lesson"] = lessons[0]
    kb = get_flip_edit_delete_back_keyboard(
        0, len(lessons), CALLBACK_LESSON_PREFIX, str(SwitchState.RETURN_PREV_CONV)
    )
    await edit_callbackquery_template(
        query,
        "lesson.jinja",
        data=lessons[0].to_dict_lesson_info(),
        keyboard=kb,
    )

    return SwitchState.CHOOSE_ACTION


@admin_required
async def all_lessons_button_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tg_id = context.user_data.get("curr_user_tg_id")
        user = await get_user_by_tg_id(tg_id)
        lessons = await get_all_lessons_from_db()
    except (UserError, LessonError) as e:
        await edit_callbackquery_template(
            update.callback_query,
            "error.jinja",
            err=str(e),
            keyboard=get_back_keyboard(SwitchState.RETURN_PREV_CONV),
        )
        return SwitchState.CHOOSE_ACTION

    kb_func = get_flip_edit_delete_back_keyboard
    await lessons_button(
        lessons=lessons,
        kb_func=kb_func,
        pattern=CALLBACK_LESSON_PREFIX,
        back_button_callbackdata=str(SwitchState.RETURN_PREV_CONV),
        template_name="lesson.jinja",
        update=update,
        context=context,
    )
    return SwitchState.CHOOSE_ACTION


@admin_required
async def delete_lesson_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = context.user_data.get("curr_user_tg_id")

    curr_lesson = context.user_data.get("curr_lesson")
    back_kb = get_back_keyboard(InterimAdminState.SHOW_ALL_LESSONS)

    if curr_lesson:
        try:
            result_message = await process_delete_lesson_admin(curr_lesson, context)
        except Error as e:
            await edit_callbackquery_template(
                update.callback_query,
                "error.jinja",
                err="Не удалось удалить занятие",
                keyboard=back_kb,
            )
            return SwitchState.CHOOSE_ACTION

    await update.callback_query.edit_message_text(
        result_message,
        reply_markup=back_kb,
    )
    return SwitchState.CHOOSE_ACTION


async def return_to_lessons_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_all_lessons_admin(update, context)
    return StopState.STOPPING
