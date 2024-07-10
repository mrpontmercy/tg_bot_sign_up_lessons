from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from handlers.response import edit_callbackquery_template, send_error_message
from services.admin.edit_lesson import (
    change_lesson_link,
    change_lesson_num_of_seats,
    change_lesson_time_start,
    change_lesson_title,
)
from services.kb import get_back_keyboard, get_edit_lesson_keyboard
from services.states import EditLesson, InterimEditLesson
from services.templates import render_template
from services.utils import (
    Lesson,
    add_message_info_into_context,
    delete_last_message_from_context,
)


async def start_edit_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    curr_lesson: Lesson | None = context.user_data.get("curr_lesson")
    back_kb = get_back_keyboard(EditLesson.RETURN_PREV_CONV)

    if curr_lesson is None:
        await edit_callbackquery_template(
            query,
            "error.jinja",
            err="Что-то пошло не так!",
            keyboard=back_kb,
        )
        return EditLesson.CHOOSE_ACTION

    # user = await get_user_by_tg_id(user_tg_id)

    # if curr_lesson.lecturer_id != user.id:
    #     await edit_callbackquery_template(
    #         query,
    #         "error.jinja",
    #         err="Что-то пошло не так!",
    #         keyboard=back_kb,
    #     )
    #     return EditLesson.CHOOSE_ACTION

    await query.edit_message_text(
        render_template(
            "edit_lesson.jinja",
            data={
                "title": curr_lesson.title,
                "time_start": curr_lesson.time_start,
                "num_of_seats": curr_lesson.num_of_seats,
                "lesson_link": curr_lesson.lesson_link,
            },
        ),
        reply_markup=get_edit_lesson_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    return EditLesson.CHOOSE_ACTION


@add_message_info_into_context
async def start_edit_title_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lesson = context.user_data.get("curr_lesson")
    back_kb = get_back_keyboard(InterimEditLesson.START_EDIT_LESSON)

    if lesson is None:
        await edit_callbackquery_template(
            query, "error.jinja", err="Не удалось найти занятие", keyboard=back_kb
        )
        return EditLesson.CHOOSE_ACTION

    await edit_callbackquery_template(
        query,
        "edit_title_lesson.jinja",
        data={"old_title": lesson.title},
        keyboard=back_kb,
    )
    return EditLesson.EDIT_TITLE


@add_message_info_into_context
async def start_edit_time_start_lesson(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    lesson = context.user_data.get("curr_lesson")
    back_kb = get_back_keyboard(InterimEditLesson.START_EDIT_LESSON)
    if lesson is None:
        await edit_callbackquery_template(
            query, "error.jinja", err="Не удалось найти занятие", keyboard=back_kb
        )
        return EditLesson.CHOOSE_ACTION

    await edit_callbackquery_template(
        query,
        "edit_time_start_lesson.jinja",
        data={"title": lesson.title, "old_time_start": lesson.time_start},
        keyboard=back_kb,
    )
    return EditLesson.EDIT_TIMESTART


@add_message_info_into_context
async def start_edit_num_of_seats_lesson(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    lesson = context.user_data.get("curr_lesson")
    back_kb = get_back_keyboard(InterimEditLesson.START_EDIT_LESSON)
    if lesson is None:
        await edit_callbackquery_template(
            query, "error.jinja", err="Не удалось найти занятие", keyboard=back_kb
        )
        return EditLesson.CHOOSE_ACTION

    if not lesson.is_group:
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            "Нельзя изменять количество мест для индивидуальных занятий!",
            reply_markup=back_kb,
        )
        return EditLesson.CHOOSE_ACTION

    await query.edit_message_text(
        "Отправьте новое количество оставшихся свободных мест на занятие!",
        reply_markup=back_kb,
    )
    return EditLesson.EDIT_NUM_OF_SEATS


@add_message_info_into_context
async def start_edit_lesson_link_lesson(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    lesson = context.user_data.get("curr_lesson")
    back_kb = get_back_keyboard(InterimEditLesson.START_EDIT_LESSON)
    if lesson is None:
        await edit_callbackquery_template(
            query, "error.jinja", err="Не удалось найти занятие", keyboard=back_kb
        )
        return EditLesson.CHOOSE_ACTION

    await edit_callbackquery_template(
        query,
        "edit_lesson_link.jinja",
        data={
            "title": lesson.title,
            "lecturer_name": lesson.lecturer_full_name,
            "old_lesson_link": lesson.lesson_link,
        },
        keyboard=back_kb,
    )
    return EditLesson.EDIT_LESSON_LINK


async def edit_title_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_tg_id = update.effective_user.id

    back_kb = get_back_keyboard(InterimEditLesson.START_EDIT_LESSON)

    err = await change_lesson_title(user_tg_id, update.effective_message.text, context)

    await delete_last_message_from_context(context)
    if not err:
        await send_error_message(
            user_tg_id, context, err="Не удалось найти урок.", keyboard=back_kb
        )
        return EditLesson.CHOOSE_ACTION

    await context.bot.send_message(
        user_tg_id,
        "Заголовок урока успешно обновлен",
        reply_markup=get_back_keyboard(EditLesson.RETURN_PREV_CONV),
    )
    return EditLesson.CHOOSE_ACTION


async def edit_time_start_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_tg_id = update.effective_user.id

    back_kb = get_back_keyboard(InterimEditLesson.START_EDIT_LESSON)
    err, message = await change_lesson_time_start(
        user_tg_id, update.message.text, context
    )

    await delete_last_message_from_context(context)
    if err:
        await send_error_message(user_tg_id, context, err=message, keyboard=back_kb)
        return EditLesson.CHOOSE_ACTION

    await context.bot.send_message(
        user_tg_id,
        "Дата занятия успешно обновлена",
        reply_markup=get_back_keyboard(EditLesson.RETURN_PREV_CONV),
    )
    return EditLesson.CHOOSE_ACTION


async def edit_num_of_seats_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_tg_id = update.effective_user.id

    err, message = await change_lesson_num_of_seats(
        user_tg_id, update.message.text, context
    )
    back_kb = get_back_keyboard(InterimEditLesson.START_EDIT_LESSON)
    await delete_last_message_from_context(context)

    if err:
        await send_error_message(user_tg_id, context, err=message, keyboard=back_kb)
        return EditLesson.CHOOSE_ACTION

    await context.bot.send_message(
        user_tg_id,
        "Количество мест на занятие успешно обновлено!",
        reply_markup=get_back_keyboard(EditLesson.RETURN_PREV_CONV),
    )

    return EditLesson.CHOOSE_ACTION


async def edit_lesson_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_tg_id = update.effective_user.id

    err, message = await change_lesson_link(user_tg_id, update.message.text, context)
    back_kb = get_back_keyboard(InterimEditLesson.START_EDIT_LESSON)
    await delete_last_message_from_context(context)
    if err:
        await send_error_message(user_tg_id, context, err=message, keyboard=back_kb)
        return EditLesson.CHOOSE_ACTION

    await context.bot.send_message(
        user_tg_id,
        "Ссылка на занятие успешно обновлена!",
        reply_markup=get_back_keyboard(EditLesson.RETURN_PREV_CONV),
    )

    return EditLesson.CHOOSE_ACTION
