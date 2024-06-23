from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from services.templates import render_template


async def notify_lesson_users(
    template_name: str,
    data: dict,
    all_students_of_lesson,
    context: ContextTypes.DEFAULT_TYPE,
):
    message_to_users = render_template(template_name, data=data, replace=False)

    for student in all_students_of_lesson:
        await context.bot.send_message(
            student.telegram_id,
            render_template("notification.jinja", data={"message": message_to_users}),
            parse_mode=ParseMode.HTML,
        )
