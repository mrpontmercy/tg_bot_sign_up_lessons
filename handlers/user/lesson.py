import logging
import sqlite3

from telegram import Update
from telegram.ext import ContextTypes

from config import (
    CALLBACK_DATA_GROUP_LESSON_PREFIX,
    CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX,
    SUB_GROUP_CODE,
    SUB_INDIVIDUAL_CODE,
)
from handlers.response import edit_callbackquery_template
from services.db import get_user_by_tg_id
from services.exceptions import LessonError, SubscriptionError, UserError
from services.kb import (
    get_back_keyboard,
    get_flip_signup_back_keyboard,
    get_type_lesson_keyboard,
)
from services.lesson import lessons_button
from services.states import InterimStartState, SwitchState
from services.user.lesson import (
    get_available_upcoming_lessons_by_type_from_db,
    get_lessons,
    process_sub_to_lesson,
)
from services.user.subscription import get_user_subscription
from services.utils import Lesson, add_start_over


@add_start_over
async def start_show_lessons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    type_lesson_kb = get_type_lesson_keyboard(SwitchState.RETURN_PREV_CONV)
    await query.edit_message_text(
        text="Выберите какой тип занятий вас интересует!",
        reply_markup=type_lesson_kb,
    )

    return SwitchState.CHOOSE_ACTION


@add_start_over
async def show_available_individual_lessons(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    user_tg_id = update.effective_user.id

    user = await get_user_by_tg_id(user_tg_id)

    context.user_data["curr_user_tg_id"] = user.telegram_id
    back_kb = get_back_keyboard(InterimStartState.SHOW_AVAILABLE_LESSONS)
    try:
        lessons = await get_available_upcoming_lessons_by_type_from_db(
            user.id, is_group=False
        )
    except LessonError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION

    context.user_data["curr_lesson"] = lessons[0]
    kb = get_flip_signup_back_keyboard(
        0,
        len(lessons),
        CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX,
        str(InterimStartState.SHOW_AVAILABLE_LESSONS),
    )
    await edit_callbackquery_template(
        query,
        "lessons_without_link.jinja",
        data=lessons[0].to_dict_lesson_info(),
        keyboard=kb,
    )

    return SwitchState.CHOOSE_ACTION


@add_start_over
async def available_individual_lessons_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    lessons, err_str = await get_lessons(
        context, get_available_upcoming_lessons_by_type_from_db, is_group=False
    )
    if lessons is None:
        await edit_callbackquery_template(
            update.callback_query,
            "error.jinja",
            err=err_str,
            keyboard=get_back_keyboard(str(InterimStartState.SHOW_AVAILABLE_LESSONS)),
        )
        return SwitchState.CHOOSE_ACTION

    kb_func = get_flip_signup_back_keyboard
    await lessons_button(
        lessons,
        kb_func,
        CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX,
        str(InterimStartState.SHOW_AVAILABLE_LESSONS),
        "lessons_without_link.jinja",
        update,
        context,
    )
    return SwitchState.CHOOSE_ACTION


@add_start_over
async def show_available_group_lessons(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    user_tg_id = update.effective_user.id

    user = await get_user_by_tg_id(user_tg_id)

    context.user_data["curr_user_tg_id"] = user.telegram_id
    back_kb = get_back_keyboard(InterimStartState.BACK_TO_START)
    try:
        lessons = await get_available_upcoming_lessons_by_type_from_db(
            user.id, is_group=True
        )
    except LessonError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION

    context.user_data["curr_lesson"] = lessons[0]
    kb = get_flip_signup_back_keyboard(
        0,
        len(lessons),
        CALLBACK_DATA_GROUP_LESSON_PREFIX,
        str(InterimStartState.SHOW_AVAILABLE_LESSONS),
    )
    await edit_callbackquery_template(
        query,
        "lessons_without_link.jinja",
        data=lessons[0].to_dict_lesson_info(),
        keyboard=kb,
    )

    return SwitchState.CHOOSE_ACTION


@add_start_over
async def available_group_lessons_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    lessons, err_str = await get_lessons(
        context, get_available_upcoming_lessons_by_type_from_db, is_group=True
    )
    if lessons is None:
        await edit_callbackquery_template(
            update.callback_query,
            "error.jinja",
            err=err_str,
            keyboard=get_back_keyboard(str(InterimStartState.SHOW_AVAILABLE_LESSONS)),
        )
        return SwitchState.CHOOSE_ACTION

    kb_func = get_flip_signup_back_keyboard
    await lessons_button(
        lessons,
        kb_func,
        CALLBACK_DATA_GROUP_LESSON_PREFIX,
        str(InterimStartState.SHOW_AVAILABLE_LESSONS),
        "lessons_without_link.jinja",
        update,
        context,
    )
    return SwitchState.CHOOSE_ACTION


async def subscribe_to_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_tg_id = update.effective_user.id
    back_kb = get_back_keyboard(str(SwitchState.RETURN_PREV_CONV))
    try:
        curr_lesson: Lesson = context.user_data.get("curr_lesson")
        if curr_lesson is None:
            await edit_callbackquery_template(
                query, "error.jinja", err="Что-то пошло не так!", keyboard=back_kb
            )
            return SwitchState.CHOOSE_ACTION
        user = await get_user_by_tg_id(user_tg_id)
        if curr_lesson.is_group:
            sub_type = SUB_GROUP_CODE
        else:
            sub_type = SUB_INDIVIDUAL_CODE
        sub_by_user_id = await get_user_subscription(user.id, sub_type)
        await process_sub_to_lesson(curr_lesson, sub_by_user_id)
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
