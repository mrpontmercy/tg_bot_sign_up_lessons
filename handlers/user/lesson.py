import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes

from config import CALLBACK_LESSON_PREFIX
from handlers.response import edit_callbackquery_template
from services.db import get_user_by_tg_id
from services.exceptions import LessonError, SubscriptionError, UserError
from services.kb import get_back_keyboard, get_flip_signup_back_keyboard
from services.lesson import _lessons_button
from services.states import InterimStartState, StartState, SwitchState
from services.user.lesson import (
    get_available_upcoming_lessons_from_db,
    get_lessons,
    process_sub_to_lesson,
)
from services.user.subscription import get_user_subscription
from services.utils import add_start_over


@add_start_over
async def show_available_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получить список всех доступных уроков, на которые пользователь еще не записан! (сортировать по дате начала занятия)
    Отобразить первый урок, добавить клавиатуру
    """
    query = update.callback_query
    await query.answer()

    user_tg_id = update.effective_user.id

    user = await get_user_by_tg_id(user_tg_id)

    context.user_data["curr_user_tg_id"] = user.telegram_id
    back_kb = get_back_keyboard(InterimStartState.BACK_TO_START)
    try:
        lessons = await get_available_upcoming_lessons_from_db(user.id)
    except LessonError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return StartState.CHOOSE_ACTION

    context.user_data["curr_lesson"] = lessons[0]
    kb = get_flip_signup_back_keyboard(
        0, len(lessons), CALLBACK_LESSON_PREFIX, str(SwitchState.RETURN_PREV_CONV)
    )
    await edit_callbackquery_template(
        query,
        "lesson.jinja",
        data=lessons[0].to_dict_lesson_info(),
        keyboard=kb,
    )

    return SwitchState.CHOOSE_ACTION


@add_start_over
async def available_lessons_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lessons, err_str = await get_lessons(
        context,
        get_available_upcoming_lessons_from_db,
    )
    if lessons is None:
        await edit_callbackquery_template(
            update.callback_query,
            "error.jinja",
            err=err_str,
            keyboard=get_back_keyboard(str(SwitchState.RETURN_PREV_CONV)),
        )
        return SwitchState.CHOOSE_ACTION

    kb_func = get_flip_signup_back_keyboard
    await _lessons_button(
        lessons,
        kb_func,
        CALLBACK_LESSON_PREFIX,
        str(SwitchState.RETURN_PREV_CONV),
        update,
        context,
    )
    return SwitchState.CHOOSE_ACTION


async def subscribe_to_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Узнаем, зарегестрирован ли текущий пользователь (если нет отправляем регистрироваться)
    Узнаем есть ли у пользователя подписка (если есть, то узнать сколько занятий осталось)(если нету, предложить оформить)
    ОБновляем значение оставшихся занятий у пользователя
    Уменьшаем количество доступных мест у занятия
    Записываем в M2M информацию о пользователе и занятии
    """
    query = update.callback_query
    await query.answer()
    user_tg_id = update.effective_user.id
    back_kb = get_back_keyboard(str(SwitchState.RETURN_PREV_CONV))
    try:
        user = await get_user_by_tg_id(user_tg_id)
        sub_by_user_id = await get_user_subscription(user.id)
        curr_lesson = context.user_data.get("curr_lesson")
        await process_sub_to_lesson(curr_lesson, sub_by_user_id)
        if curr_lesson is None:
            await edit_callbackquery_template(
                query, "error.jinja", err="Что-то пошло не так!", keyboard=back_kb
            )
            return SwitchState.CHOOSE_ACTION
    except (UserError, SubscriptionError, LessonError) as err:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(err), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION
    except sqlite3.Error as e:
        logging.getLogger(__name__).exception(e)
        await query.edit_message_text(
            "Что-то пошло не так, не удалось записаться на занятие.\nОбратитесь к администратору!",
            reply_markup=back_kb,
        )
        return SwitchState.CHOOSE_ACTION

    del context.user_data["curr_lesson"]
    await query.edit_message_text(
        "Вы успешно записались на занятие!", reply_markup=back_kb
    )

    return SwitchState.CHOOSE_ACTION
