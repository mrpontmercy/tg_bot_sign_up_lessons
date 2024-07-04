from datetime import datetime, timedelta, timezone
from sqlite3 import Error

from config import DATETIME_FORMAT
from db import fetch_all, get_db
from services.db import execute_delete, execute_update
from services.exceptions import LessonError
from services.utils import Lesson, Subscription, TLSubscription


async def fetch_all_user_upcoming_lessons(user_id: str | int, is_group: bool):
    sql = """select l.id, l.title, l.time_start, l.num_of_seats, u.f_name || ' ' || u.s_name as lecturer_full_name, l.lecturer_id, l.lesson_link from lesson l
            join user_lesson ul on l.id=ul.lesson_id join user u on u.id=l.lecturer_id WHERE ul.user_id=:user_id AND strftime('%Y-%m-%d %H:%M', 'now', '4 hours') < l.time_start 
            AND l.is_group=:is_group"""  # не * а конкретные поля
    params = {
        "user_id": user_id,
        "is_group": is_group,
    }
    return await fetch_all(sql, params=params)


async def get_user_upcoming_lessons_by_type(user_id, is_group: bool) -> list[Lesson]:
    lessons = await fetch_all_user_upcoming_lessons(user_id, is_group)

    if lessons is None or not lessons:
        raise LessonError("Не удалось найти занятия пользователя!")

    res = []

    for row in lessons:
        res.append(Lesson(**row))

    return res


def is_possible_dt(lesson_start_dt):
    lesson_dt_utc = datetime.strptime(lesson_start_dt, DATETIME_FORMAT) - timedelta(
        hours=4
    )
    user_dt_utc = datetime.now(timezone.utc)
    user_dt_utc = datetime(
        user_dt_utc.year,
        user_dt_utc.month,
        user_dt_utc.day,
        user_dt_utc.hour,
        user_dt_utc.minute,
    )
    res = lesson_dt_utc - user_dt_utc
    if res.total_seconds() // 3600 < 2:
        return False
    return True


async def update_individual_lesson_after_cancel(
    lesson: Lesson, user_id: int, num_of_classes: int
):
    try:
        await execute_update(
            "lesson",
            "num_of_seats=:num_of_seats",
            "id=:l_id",
            {"num_of_seats": lesson.num_of_seats + 1, "l_id": lesson.id},
            autocommit=False,
        )

        await execute_update(
            "subscription",
            "num_of_classes=:num_of_classes",
            "user_id=:user_id",
            {"num_of_classes": num_of_classes + 1, "user_id": user_id},
            autocommit=False,
        )

        await execute_delete(
            "user_lesson",
            "lesson_id=:lesson_id AND user_id=:user_id",
            {"user_id": user_id, "lesson_id": lesson.id},
            autocommit=False,
        )
    except Error:
        await (await get_db()).rollback()
        raise

    await (await get_db()).commit()


async def update_group_lesson_after_cancel(
    lesson: Lesson, user_id: int, num_of_classes: int
):
    try:
        await execute_update(
            "lesson",
            "num_of_seats=:num_of_seats",
            "id=:l_id",
            {"num_of_seats": lesson.num_of_seats + 1, "l_id": lesson.id},
            autocommit=False,
        )

        await execute_update(
            "tl_subscription",
            "num_of_classes=:num_of_classes",
            "user_id=:user_id",
            {"num_of_classes": num_of_classes + 1, "user_id": user_id},
            autocommit=False,
        )

        await execute_delete(
            "user_lesson",
            "lesson_id=:lesson_id AND user_id=:user_id",
            {"user_id": user_id, "lesson_id": lesson.id},
            autocommit=False,
        )
    except Error:
        await (await get_db()).rollback()
        raise

    await (await get_db()).commit()


async def update_db_info_after_cancel_lesson(
    lesson: Lesson, sub: Subscription | TLSubscription, user_id: int
):
    try:
        if isinstance(sub, Subscription):
            await update_individual_lesson_after_cancel(
                lesson, user_id, sub.num_of_classes
            )
        elif isinstance(sub, TLSubscription):
            await update_group_lesson_after_cancel(lesson, user_id, sub.num_of_classes)
    except Error:
        raise
