import re
from telegram.ext import ContextTypes

from handlers.response import send_error_message
from services.admin.subscription import validate_num_of_classes
from services.db import execute_update, get_all_users_of_lesson
from services.exceptions import InputMessageError
from services.notification import (
    notify_users_and_lecturer_changing_lesson,
    notify_users_changing_lesson,
)
from services.utils import DATE_TIME_PATTERN, URL_PATTERN, Lesson


async def change_lesson_title(
    user_tg_id, message: str, context: ContextTypes.DEFAULT_TYPE
):
    curr_lesson: Lesson | None = context.user_data.get("curr_lesson", None)

    if curr_lesson is None:
        return False

    new_title = " ".join(message.split(" "))

    data = {
        "old_title": curr_lesson.title,
        "new_title": new_title,
        "time_start": curr_lesson.time_start,
    }

    await execute_update(
        "lesson",
        "title=:title",
        "lecturer_id=:lecturer_id AND id=:lesson_id",
        params={
            "title": new_title,
            "lecturer_id": curr_lesson.lecturer_id,
            "lesson_id": curr_lesson.id,
        },
    )

    # await notify_users_and_lecturer_changing_lesson(
    #     "edit_title_lesson.jinja", curr_lesson.id, curr_lesson.lecturer_id, data, context
    # )
    return True


async def change_lesson_time_start(
    user_tg_id, message: str, context: ContextTypes.DEFAULT_TYPE
):
    curr_lesson: Lesson | None = context.user_data.get("curr_lesson", None)

    if curr_lesson is None:
        await send_error_message(user_tg_id, context, err="Не удалось найти урок")
        return True, "Не удалось найти урок"

    validated_time_start = _validate_datetime(message)

    if not validated_time_start:
        return True, "Неверный формат даты и времени!\nПопробуйте снова."

    data = {
        "title": curr_lesson.title,
        "old_time_start": curr_lesson.time_start,
        "new_time_start": validated_time_start,
    }

    await execute_update(
        "lesson",
        "time_start=:time_start",
        "lecturer_id=:lecturer_id AND id=:lesson_id",
        params={
            "time_start": message,
            "lecturer_id": curr_lesson.lecturer_id,
            "lecturer_name": curr_lesson.lecturer_full_name,
            "lesson_id": curr_lesson.id,
        },
    )

    # await notify_users_and_lecturer_changing_lesson(
    #     "notify_edit_time_start_lesson.jinja", curr_lesson.id, curr_lesson.lecturer_id, data, context
    # )
    return False, None


async def change_lesson_num_of_seats(
    user_tg_id, message: str, context: ContextTypes.DEFAULT_TYPE
):
    curr_lesson: Lesson | None = context.user_data.get("curr_lesson", None)

    if curr_lesson is None:
        await send_error_message(user_tg_id, context, err="Не удалось найти урок")
        return True, "Не удалось найти урок"

    try:
        num_of_seats = validate_num_of_classes(message)
    except InputMessageError as e:
        return True, str(e)

    await execute_update(
        "lesson",
        "num_of_seats=:num_of_seats",
        "lecturer_id=:lecturer_id AND id=:lesson_id",
        params={
            "num_of_seats": num_of_seats,
            "lecturer_id": curr_lesson.lecturer_id,
            "lesson_id": curr_lesson.id,
        },
    )
    data = {
        "title": curr_lesson.title,
        "lecturer_name": curr_lesson.lecturer_full_name,
        "num_of_seats": num_of_seats,
    }

    # await notify_users_and_lecturer_changing_lesson(
    #     "notify_edit_num_of_seats_lesson.jinja", curr_lesson.id, curr_lesson.lecturer_id, data, context
    # )

    return False, None


async def change_lesson_link(
    user_tg_id, message: str, context: ContextTypes.DEFAULT_TYPE
):
    curr_lesson: Lesson | None = context.user_data.get("curr_lesson", None)

    if curr_lesson is None:
        await send_error_message(user_tg_id, context, err="Не удалось найти урок")
        return True, "Не удалось найти урок"

    try:
        link = _validate_lesson_link(message)
    except InputMessageError as e:
        return True, str(e)

    await execute_update(
        "lesson",
        "lesson_link=:lesson_link",
        "lecturer_id=:lecturer_id AND id=:lesson_id",
        params={
            "lesson_link": link,
            "lecturer_id": curr_lesson.lecturer_id,
            "lesson_id": curr_lesson.id,
        },
    )
    data = {
        "title": curr_lesson.title,
        "lecturer_name": curr_lesson.lecturer_full_name,
        "lesson_link": link,
    }

    # await notify_users_and_lecturer_changing_lesson(
    #     "notify_edit_lesson_link.jinja", curr_lesson.id, curr_lesson.lecturer_id, data, context
    # )

    return False, None


def _validate_lesson_link(link: str):
    link = link.split(" ")
    if len(link) != 1:
        raise InputMessageError("Количество слов в сообщение должно быть равным 1")

    if not re.fullmatch(URL_PATTERN, link[0], flags=re.I):
        raise InputMessageError("Сообщение должно содержать только ссылку на занятие")

    return link[0]


def _validate_datetime(message: str):
    if re.fullmatch(DATE_TIME_PATTERN, message):
        return True
    return False
