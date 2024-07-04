import csv
import logging
from pathlib import Path
from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes

from db import execute, fetch_all
from handlers.response import edit_callbackquery_template
from services.exceptions import ColumnCSVError, LessonError
from services.utils import Lesson, TransientLesson


async def lessons_button(
    lessons: list[Lesson],
    kb_func: Callable,
    pattern: str,
    back_button_callbackdata: str,
    template_name: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()
    current_index = int(query.data[len(pattern) :])
    context.user_data["curr_lesson"] = lessons[current_index]
    kb = kb_func(current_index, len(lessons), pattern, back_button_callbackdata)
    await edit_callbackquery_template(
        update.callback_query,
        template_name,
        data=lessons[current_index].to_dict_lesson_info(),
        keyboard=kb,
    )


def get_lessons_from_file(
    file_path: Path,
    fieldnames: tuple[str] = (
        "title",
        "time_start",
        "num_of_seats",
        "lecturer_phone",
        "lesson_link",
        "is_group",
    ),
) -> list[TransientLesson] | None:
    lessons: list[TransientLesson] = []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, fieldnames)
        for row in reader:
            try:
                lesson = TransientLesson(**row)
            except (TypeError, KeyError, ColumnCSVError) as e:
                logging.getLogger(__name__).exception(e)
                return None
            except Exception as e:
                logging.getLogger(__name__).exception(e)
                return None
            else:
                lessons.append(lesson)

    return lessons


async def insert_lesson_in_db(params):
    await execute(
        """INSERT INTO lesson (title, time_start, num_of_seats, lecturer_id) VALUES (:title, :time_start,:num_of_seats, :lecturer_id)""",
        params,
    )


async def get_all_lessons_by_type_from_db(*, is_group: bool) -> list[Lesson]:
    sql = """select l.id, l.title, l.time_start, l.num_of_seats, u.f_name || ' ' || u.s_name as lecturer_full_name, l.lecturer_id, l.lesson_link, l.is_group from lesson l
            join user u on u.id=l.lecturer_id WHERE l.is_group=:is_group"""
    params = {"is_group": is_group}
    rows = await fetch_all(sql, params=params)

    if not rows:
        raise LessonError("Не удалось найти занятия")

    return [Lesson(**row) for row in rows]
