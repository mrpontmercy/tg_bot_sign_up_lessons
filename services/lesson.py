import csv
import logging
from pathlib import Path
from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes
from db import execute
from handlers.response import edit_callbackquery_template
from services.exceptions import ColumnCSVError
from services.templates import render_template
from services.utils import Lesson, TransientLesson


async def _lessons_button(
    lessons: list[Lesson],
    kb_func: Callable,
    pattern: str,
    back_button_callbackdata: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Ответить на колбекквери (чтобы кнопка не отображалась нажатой)
    Получаем список всех уроков
    Формируем новую клавиатуру
    """
    query = update.callback_query
    await query.answer()
    current_index = int(query.data[len(pattern) :])
    context.user_data["curr_lesson"] = lessons[current_index]
    kb = kb_func(current_index, len(lessons), pattern, back_button_callbackdata)
    await edit_callbackquery_template(
        update.callback_query,
        "lesson.jinja",
        data=lessons[current_index].to_dict_lesson_info(),
        keyboard=kb,
    )


def get_lessons_from_file(
    file_path: Path,
    fieldnames: tuple[str] = ("title", "time_start", "num_of_seats", "lecturer_phone"),
) -> list[TransientLesson] | None:
    lessons: list[TransientLesson] = []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, fieldnames)
        for row in reader:
            try:
                l = TransientLesson(**row)
            except (TypeError, KeyError, ColumnCSVError) as e:
                logging.getLogger(__name__).exception(e)
                return None
            except Exception as e:
                logging.getLogger(__name__).exception(e)
                return None
            else:
                lessons.append(l)

    return lessons


async def insert_lesson_in_db(params):
    await execute(
        """INSERT INTO lesson (title, time_start, num_of_seats, lecturer_id) VALUES (:title, :time_start,:num_of_seats, :lecturer_id)""",
        params,
    )
