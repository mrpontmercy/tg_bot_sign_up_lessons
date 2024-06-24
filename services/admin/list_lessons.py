import logging
from sqlite3 import Error

from telegram.ext import ContextTypes
from db import get_db
from services.db import execute_delete, execute_update, get_all_users_of_lesson
from services.notification import notify_users_and_lecturer_changing_lesson
from services.utils import Lesson


async def process_delete_lesson_db(lesson_id):
    params = {"lesson_id": lesson_id}
    try:
        await execute_update(
            "subscription",
            "num_of_classes=num_of_classes + 1",
            "user_id IN (SELECT user_id from user_lesson where lesson_id=:lesson_id)",
            params=params,
            autocommit=False,
        )

        await execute_delete("lesson", "id=:lesson_id", params=params, autocommit=False)
    except Error as e:
        logging.getLogger(__name__).exception(e)
        await (await get_db()).rollback()
        raise
    await (await get_db()).commit()


async def process_delete_lesson_admin(
    lesson: Lesson, context: ContextTypes.DEFAULT_TYPE
):
    try:
        await process_delete_lesson_db(lesson.id)
    except Error:
        raise

    all_students_of_lesson = await get_all_users_of_lesson(lesson.id)

    if all_students_of_lesson is None:
        return "Нет записанных студентов.\nЗанятие успешно отменено."

    data = {
        "title": lesson.title,
        "time_start": lesson.time_start,
        "lecturer": lesson.lecturer_full_name,
    }

    # await notify_users_and_lecturer_changing_lesson(
    #     "cancel_lesson_message.jinja", lesson.id, lesson.lecturer_id, data, context
    # )

    return "Урок успешно отменен. "
