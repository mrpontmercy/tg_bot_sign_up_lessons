from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from services.db import get_all_users_of_lesson
from services.templates import render_template


async def notify_users_changing_lesson(
    template_name: str,
    lesson_id: int,
    data: dict,
    context: ContextTypes.DEFAULT_TYPE,
):
    all_students_of_lesson = await get_all_users_of_lesson(lesson_id)

    message_to_users = render_template(template_name, data=data, replace=False)

    if all_students_of_lesson:
        for student in all_students_of_lesson:
            await context.bot.send_message(
                student.telegram_id,
                render_template(
                    "notification.jinja", data={"message": message_to_users}
                ),
                parse_mode=ParseMode.HTML,
            )


async def notify_users_and_lecturer_changing_lesson(
    template_name: str,
    lesson_id: int,
    lecturer_id: int,
    data: dict,
    context: ContextTypes.DEFAULT_TYPE,
):
    all_users_of_lesson = await get_all_users_of_lesson(lesson_id)

    message_to_users = render_template(template_name, data=data, replace=False)

    all_users_of_lesson += [lecturer_id]

    if all_users_of_lesson:
        for student in all_users_of_lesson:
            await context.bot.send_message(
                student.telegram_id,
                render_template(
                    "notification.jinja", data={"message": message_to_users}
                ),
                parse_mode=ParseMode.HTML,
            )
