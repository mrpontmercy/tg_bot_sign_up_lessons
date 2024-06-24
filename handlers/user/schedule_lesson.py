import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes

from config import CALLBACK_USER_LESSON_PREFIX
from handlers.response import edit_callbackquery_template
from services.db import get_user_by_tg_id
from services.exceptions import LessonError, SubscriptionError
from services.kb import get_back_keyboard, get_flip_cancel_back_keyboard
from services.lesson import lessons_button
from services.states import InterimStartState, SwitchState
from services.user.lesson import get_lessons
from services.user.schedule_lesson import (
    get_user_upcoming_lessons,
    is_possible_dt,
    update_db_info_after_cancel_lesson,
)
from services.utils import Lesson, add_start_over


@add_start_over
async def show_schedule_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отображать уроки, на которые записан пользователь

    узнать есть ли пользователь в бд
    узнать есть ли у него уроки
    """
    query = update.callback_query
    await query.answer()

    user_tg_id = update.effective_user.id

    user = await get_user_by_tg_id(user_tg_id)

    context.user_data["curr_user_tg_id"] = user.telegram_id

    back_kb = get_back_keyboard(SwitchState.RETURN_PREV_CONV)
    try:
        lessons_by_user = await get_user_upcoming_lessons(user.id)
    except LessonError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION

    first_lesson: Lesson = lessons_by_user[0]
    context.user_data["curr_lesson"] = first_lesson
    kb = get_flip_cancel_back_keyboard(
        0,
        len(lessons_by_user),
        CALLBACK_USER_LESSON_PREFIX,
        str(SwitchState.RETURN_PREV_CONV),
    )
    await edit_callbackquery_template(
        query,
        "lesson.jinja",
        data=first_lesson.to_dict_lesson_info(),
        keyboard=kb,
    )
    return SwitchState.CHOOSE_ACTION


@add_start_over
async def schedule_lessons_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lessons, state = await get_lessons(
        context,
        get_user_upcoming_lessons,
    )

    if lessons is None:
        return state

    kb_func = get_flip_cancel_back_keyboard
    await lessons_button(
        lessons=lessons,
        kb_func=kb_func,
        pattern=CALLBACK_USER_LESSON_PREFIX,
        back_button_callbackdata=str(SwitchState.RETURN_PREV_CONV),
        update=update,
        context=context,
    )
    return SwitchState.CHOOSE_ACTION


async def cancel_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    отменять не поздее чем за 2 часа до занятия

    Обновить информацию в таблице lesson
    обновить количество уроков в абонименте
    удалить строчку из user_lesson
    """
    query = update.callback_query
    await query.answer()

    user_tg_id = update.effective_user.id
    back_kb = get_back_keyboard(SwitchState.RETURN_PREV_CONV)
    back_to_lesson_kb = get_back_keyboard(InterimStartState.SHOW_SCHEDULE_LESSONS)
    lesson: Lesson | None = context.user_data.get("curr_lesson")
    if lesson is None:
        await edit_callbackquery_template(
            query,
            "error.jinja",
            err="Не удалось удалить урок, попробуйте снова!",
            keyboard=back_kb,
        )
        return SwitchState.CHOOSE_ACTION

    if not is_possible_dt(lesson.time_start):
        await update.callback_query.edit_message_text(
            "До занятия осталось меньше 2х часов. Отменить занятие не получится!",
            reply_markup=back_to_lesson_kb,
        )
        return SwitchState.CHOOSE_ACTION

    user = await get_user_by_tg_id(user_tg_id)
    try:
        await update_db_info_after_cancel_lesson(lesson, user.id)
    except SubscriptionError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION
    except sqlite3.Error as e:
        logging.getLogger(__name__).exception(e)
        await edit_callbackquery_template(
            query,
            "error.jinja",
            err="Что-то пошло не так, не удалось записаться на занятие.\nОбратитесь к администратору!",
            keyboard=back_kb,
        )
        return SwitchState.CHOOSE_ACTION

    lecturer_id = lesson.lecturer_id
    # await notify_lecturer_user_cancel_lesson(
    #     f"{user.f_name} {user.s_name}", lecturer_id, lesson, context
    # )
    await update.callback_query.edit_message_text(
        "Занятие успешно отменено!", reply_markup=back_kb
    )
    return SwitchState.CHOOSE_ACTION
