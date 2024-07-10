from sqlite3 import Error

from telegram import Update
from telegram.ext import ContextTypes

from config import (
    ADMIN_STATUS,
    CALLBACK_DATA_GROUP_LESSON_PREFIX,
    CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX,
    LECTURER_STATUS,
)
from handlers.response import edit_callbackquery_template
from services.admin.list_lessons import (
    process_delete_lesson_admin,
)
from services.db import get_lecturer_upcomming_lessons, get_user_by_tg_id
from services.exceptions import LessonError, UserError
from services.filters import is_admin
from services.kb import (
    get_back_keyboard,
    get_flip_edit_delete_back_keyboard,
    get_type_lesson_keyboard,
)
from services.lesson import lessons_button, get_all_lessons_by_type_from_db
from services.states import InterimAdminState, StopState, SwitchState
from services.utils import Lesson


async def start_show_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    type_lesson_kb = get_type_lesson_keyboard(SwitchState.RETURN_PREV_CONV)

    await query.edit_message_text(
        text="Выберите какой тип занятий хотите посмотреть", reply_markup=type_lesson_kb
    )

    return SwitchState.CHOOSE_ACTION


async def show_all_group_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_tg_id = update.effective_user.id
    context.user_data["curr_user_tg_id"] = user_tg_id

    back_kb = get_back_keyboard(SwitchState.START_SHOW_RESOURCES)
    try:
        user = await get_user_by_tg_id(user_tg_id)
        user_is_admin = is_admin(user_tg_id)
        if user_is_admin:
            lessons = await get_all_lessons_by_type_from_db(is_group=True)
        elif not user_is_admin and user.status == LECTURER_STATUS:
            lessons = await get_lecturer_upcomming_lessons(user.id, is_group=True)
    except (LessonError, UserError) as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION

    context.user_data["curr_lesson"] = lessons[0]
    kb = get_flip_edit_delete_back_keyboard(
        0,
        len(lessons),
        CALLBACK_DATA_GROUP_LESSON_PREFIX,
        str(SwitchState.START_SHOW_RESOURCES),
    )
    await edit_callbackquery_template(
        query,
        "lesson.jinja",
        data=lessons[0].to_dict_lesson_info(),
        keyboard=kb,
    )

    return SwitchState.CHOOSE_ACTION


async def all_group_lessons_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tg_id = context.user_data.get("curr_user_tg_id")
        user = await get_user_by_tg_id(tg_id)
        user_is_admin = is_admin(tg_id)
        if user_is_admin:
            lessons = await get_all_lessons_by_type_from_db(is_group=True)
        elif not user_is_admin and user.status == LECTURER_STATUS:
            lessons = await get_lecturer_upcomming_lessons(user.id, is_group=True)
    except (UserError, LessonError) as e:
        await edit_callbackquery_template(
            update.callback_query,
            "error.jinja",
            err=str(e),
            keyboard=get_back_keyboard(SwitchState.START_SHOW_RESOURCES),
        )
        return SwitchState.CHOOSE_ACTION

    kb_func = get_flip_edit_delete_back_keyboard
    await lessons_button(
        lessons=lessons,
        kb_func=kb_func,
        pattern=CALLBACK_DATA_GROUP_LESSON_PREFIX,
        back_button_callbackdata=str(SwitchState.START_SHOW_RESOURCES),
        template_name="lesson.jinja",
        update=update,
        context=context,
    )
    return SwitchState.CHOOSE_ACTION


async def show_all_individual_lessons(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Получить список всех доступных уроков, на которые пользователь еще не записан! (сортировать по дате начала занятия)
    Отобразить первый урок, добавить клавиатуру
    """

    query = update.callback_query
    await query.answer()

    user_tg_id = update.effective_user.id

    context.user_data["curr_user_tg_id"] = user_tg_id

    back_kb = get_back_keyboard(SwitchState.START_SHOW_RESOURCES)
    try:
        user = await get_user_by_tg_id(user_tg_id)
        user_is_admin = is_admin(user_tg_id)
        if user_is_admin:
            lessons = await get_all_lessons_by_type_from_db(is_group=False)
        elif not user_is_admin and user.status == LECTURER_STATUS:
            lessons = await get_lecturer_upcomming_lessons(user.id, is_group=False)
    except LessonError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION

    context.user_data["curr_lesson"] = lessons[0]
    kb = get_flip_edit_delete_back_keyboard(
        0,
        len(lessons),
        CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX,
        str(SwitchState.START_SHOW_RESOURCES),
    )
    await edit_callbackquery_template(
        query,
        "lesson.jinja",
        data=lessons[0].to_dict_lesson_info(),
        keyboard=kb,
    )

    return SwitchState.CHOOSE_ACTION


async def all_individual_lessons_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        tg_id = context.user_data.get("curr_user_tg_id")
        user = await get_user_by_tg_id(tg_id)
        user_is_admin = is_admin(tg_id)
        if user_is_admin:
            lessons = await get_all_lessons_by_type_from_db(is_group=False)
        elif not user_is_admin and user.status == LECTURER_STATUS:
            lessons = await get_lecturer_upcomming_lessons(user.id, is_group=False)
    except (UserError, LessonError) as e:
        await edit_callbackquery_template(
            update.callback_query,
            "error.jinja",
            err=str(e),
            keyboard=get_back_keyboard(SwitchState.START_SHOW_RESOURCES),
        )
        return SwitchState.CHOOSE_ACTION

    kb_func = get_flip_edit_delete_back_keyboard
    await lessons_button(
        lessons=lessons,
        kb_func=kb_func,
        pattern=CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX,
        back_button_callbackdata=str(SwitchState.START_SHOW_RESOURCES),
        template_name="lesson.jinja",
        update=update,
        context=context,
    )
    return SwitchState.CHOOSE_ACTION


async def delete_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    curr_lesson: Lesson = context.user_data.get("curr_lesson")
    back_kb = get_back_keyboard(SwitchState.START_SHOW_RESOURCES)
    user_tg_id = update.effective_user.id

    if curr_lesson:
        try:
            user = await get_user_by_tg_id(user_tg_id)
            user_is_admin = is_admin(user_tg_id)
            if curr_lesson.lecturer_id != user.id:
                raise UserError("Это занятие не относится к вам!")
            if user_is_admin:
                status = ADMIN_STATUS
            else:
                status = LECTURER_STATUS
            result_message = await process_delete_lesson_admin(
                curr_lesson, context, status
            )
        except UserError as e:
            await edit_callbackquery_template(
                update.callback_query,
                "error.jinja",
                err=str(e),
                keyboard=back_kb,
            )
            return SwitchState.CHOOSE_ACTION
        except Error:
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


async def return_to_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    curr_lesson: Lesson | None = context.user_data.get("curr_lesson", None)
    if curr_lesson.is_group:
        await show_all_group_lessons(update, context)
    else:
        await show_all_individual_lessons(update, context)
    return StopState.STOPPING
