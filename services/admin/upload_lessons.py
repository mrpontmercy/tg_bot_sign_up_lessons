import logging
import os
from sqlite3 import Error
from telegram import Document
from telegram.ext import ContextTypes

from config import LECTURER_STATUS
from db import get_db
from services.db import get_user_by_phone_number, insert_lesson_in_db
from services.exceptions import UserError
from services.lesson import get_lessons_from_file
from services.utils import TransientLesson, get_saved_lessonfile_path, make_lesson_params


async def get_lecturer_and_error_by_phone(phone_number):
    try:
        lecturer = await get_user_by_phone_number(phone_number)
    except UserError:
        return None, f"Нет пользователя с номером {phone_number}"
    else:
        if lecturer.status != LECTURER_STATUS:
            return (
                None,
                f"Пользователь с номером {phone_number} не является преподавателем",
            )

    return lecturer, None


async def insert_lessons_if_possible_db(lessons: list[TransientLesson], is_group: bool):
    "Добавление уроков в бд в зависимости от типа занятия is_group=True - Групповое, is_group=False - индивидуальное"
    res_err = []

    for lesson in lessons:
        lecturer, message = await get_lecturer_and_error_by_phone(lesson.lecturer_phone)
        if message is not None:
            res_err.append((message, lesson.title))
            continue

        params = make_lesson_params(lesson, lecuturer_id=lecturer.id, is_group=is_group)
        try:
            await insert_lesson_in_db(params)
        except Error as e:
            logging.getLogger(__name__).exception(e)
            await (await get_db()).rollback()
            res_err.append(("Серьезная ошибка", lesson.title))
    return res_err


async def process_insert_lesson_into_db(
    recieved_file: Document,
    user_tg_id: int,
    is_group: bool,
    context: ContextTypes.DEFAULT_TYPE,
):
    file_path = await get_saved_lessonfile_path(recieved_file, context)

    lessons = get_lessons_from_file(file_path)
    os.remove(file_path)
    if lessons is None or not lessons:
        return (
            False,
            "Неверно заполнен файл. Возможно файл пустой. Попробуй с другим файлом.",
        )
    errors_after_inserting_lessons = await insert_lessons_if_possible_db(
        lessons, is_group
    )

    if errors_after_inserting_lessons:
        await context.bot.send_message(
            user_tg_id,
            "\n".join([row[0] for row in errors_after_inserting_lessons]),
        )

    err_lesson = ";\n".join([row[-1] for row in errors_after_inserting_lessons])
    if len(lessons) == len(errors_after_inserting_lessons):
        answer = "Ни одного занятия не было добавлено!"
    else:
        answer = (
            f"Все занятия, кроме\n<b>{err_lesson}</b>\nбыли добавлены в общий список"
        )
    return True, answer
