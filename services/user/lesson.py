from sqlite3 import Error
from telegram.ext import ContextTypes
from db import fetch_all, fetch_one, get_db
from services.db import execute_insert, execute_update, get_user_by_tg_id, select_where
from services.exceptions import LessonError, UserError
from services.utils import Lesson, Subscription


async def get_available_upcoming_lessons_from_db(user_id: int):
    sql = """select l.id, l.title, l.time_start, l.num_of_seats, u.f_name || ' ' || u.s_name as lecturer_full_name, l.lecturer_id from lesson l 
            left join user_lesson ul on ul.lesson_id=l.id AND ul.user_id=:user_id join user u on u.id=l.lecturer_id 
            WHERE ul.lesson_id is NULL AND strftime("%Y-%m-%d %H:%M", "now", "4 hours") < l.time_start"""

    # select l.id, l.title, l.time_start, l.num_of_seats, l.lecturer_id, u.f_name from lesson l join user_lesson ul on ul.lesson_id=l.id AND ul.user_id=1 left join user u on u.id=l.lecturer_id WHERE ul.lesson_
    #     id is not NULL;
    rows = await fetch_all(sql, params={"user_id": user_id})
    if not rows:
        raise LessonError("Не удалось найти занятия")
    lessons: list[Lesson] = []
    for row in rows:
        lessons.append(Lesson(**row))

    return lessons


async def get_lessons(context: ContextTypes.DEFAULT_TYPE, get_lessons_from_db_func):
    user_tg_id = context.user_data.get("curr_user_tg_id")
    if user_tg_id is None:
        return None, "Что-то пошло не так"
    try:
        user = await get_user_by_tg_id(user_tg_id)
        lessons = await get_lessons_from_db_func(user.id)
    except (LessonError, UserError) as e:
        return None, str(e)

    return lessons, None


async def already_subscribed_to_lesson(lesson_id, user_id):
    sql = select_where("user_lesson", "id", "user_id=:user_id AND lesson_id=:lesson_id")
    is_subscribed = await fetch_one(sql, {"user_id": user_id, "lesson_id": lesson_id})
    if is_subscribed is None:
        return False
    return True


async def process_sub_to_lesson(lesson: Lesson, sub: Subscription):
    is_subscribed = await already_subscribed_to_lesson(lesson.id, sub.user_id)
    if is_subscribed:
        raise LessonError("Вы уже записались на это занятие!")
    try:
        await execute_update(
            "lesson",
            "num_of_seats=:seats_left",
            "id=:lesson_id",
            {
                "seats_left": lesson.num_of_seats - 1,
                "lesson_id": lesson.id,
            },
            autocommit=False,
        )
        await execute_update(
            "subscription",
            "num_of_classes=:num_class_left",
            "user_id=:user_id",
            {
                "num_class_left": sub.num_of_classes - 1,
                "user_id": sub.user_id,
            },
            autocommit=False,
        )
        await execute_insert(
            "user_lesson",
            "user_id, lesson_id",
            ":user_id, :lesson_id",
            {
                "user_id": sub.user_id,
                "lesson_id": lesson.id,
            },
            autocommit=False,
        )
    except Error as e:
        await (await get_db()).rollback()
        raise
    await (await get_db()).commit()
