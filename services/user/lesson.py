from datetime import datetime
from sqlite3 import Error

from telegram.ext import ContextTypes

from db import fetch_all, fetch_one, get_db
from services.db import execute_insert, execute_update, get_user_by_tg_id, select_where
from services.exceptions import LessonError, SubscriptionError, UserError
from services.utils import Lesson, Subscription, TLSubscription


async def get_available_upcoming_lessons_by_type_from_db(user_id: int, is_group: bool):
    sql = """select l.id, l.title, l.time_start, l.num_of_seats, u.f_name || ' ' || u.s_name as lecturer_full_name, l.lecturer_id, l.lesson_link, l.is_group from lesson l 
            left join user_lesson ul on ul.lesson_id=l.id AND ul.user_id=:user_id join user u on u.id=l.lecturer_id 
            WHERE ul.lesson_id is NULL AND strftime("%Y-%m-%d %H:%M", "now", "4 hours") < l.time_start AND l.is_group=:is_group AND l.num_of_seats > 0"""

    # select l.id, l.title, l.time_start, l.num_of_seats, l.lecturer_id, u.f_name from lesson l join user_lesson ul on ul.lesson_id=l.id AND ul.user_id=1 left join user u on u.id=l.lecturer_id WHERE ul.lesson_
    #     id is not NULL;
    params = {
        "user_id": user_id,
        "is_group": is_group,
    }
    rows = await fetch_all(sql, params=params)
    if not rows:
        raise LessonError("Не удалось найти занятия")
    lessons: list[Lesson] = []
    for row in rows:
        lessons.append(Lesson(**row))

    return lessons


async def get_lessons(
    context: ContextTypes.DEFAULT_TYPE, get_lessons_from_db_func, is_group: bool
):
    user_tg_id = context.user_data.get("curr_user_tg_id")
    if user_tg_id is None:
        return None, "Что-то пошло не так"
    try:
        user = await get_user_by_tg_id(user_tg_id)
        lessons = await get_lessons_from_db_func(user.id, is_group)
    except (LessonError, UserError) as e:
        return None, str(e)

    return lessons, None


async def already_subscribed_to_lesson(lesson_id, user_id):
    sql = select_where("user_lesson", "id", "user_id=:user_id AND lesson_id=:lesson_id")
    is_subscribed = await fetch_one(sql, {"user_id": user_id, "lesson_id": lesson_id})
    if is_subscribed is None:
        return False
    return True


async def sub_to_individual_lesson(lesson: Lesson, sub: Subscription):
    is_subscribed = await already_subscribed_to_lesson(lesson.id, sub.user_id)
    if is_subscribed:
        raise LessonError("Вы уже записаны на это занятие!")
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
    except Error:
        await (await get_db()).rollback()
        raise
    await (await get_db()).commit()


def is_active_group_subscription(sub: TLSubscription):
    not_started = datetime.date(
        datetime.strptime(sub.start_date, "%Y-%m-%d")
    ) <= datetime.date(datetime.now())
    not_over = datetime.date(
        datetime.strptime(sub.end_date, "%Y-%m-%d")
    ) >= datetime.date(datetime.now())

    if not_started and not_over:
        return True
    return False


def is_possible_to_subscribe(sub_end_date: str, lesson_start_date: str):
    is_possible = datetime.date(
        datetime.strptime(sub_end_date, "%Y-%m-%d")
    ) > datetime.date(datetime.strptime(lesson_start_date, "%Y-%m-%d %H:%M"))
    return is_possible


async def sub_to_group_lesson(lesson: Lesson, sub: Subscription | TLSubscription):
    is_subscribed = await already_subscribed_to_lesson(lesson.id, sub.user_id)
    if is_subscribed:
        raise LessonError("Вы уже записаны на это занятие!")
    if not is_active_group_subscription(sub):
        raise SubscriptionError("Ваш групповой абонемент недействителен.")

    if not is_possible_to_subscribe(sub.end_date, lesson.time_start):
        raise SubscriptionError(
            "Ваша групповая подписка закончится к моменту начала занятия. Невозможно записаться на данное занятие."
        )
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
            "tl_subscription",
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
    except Error:
        await (await get_db()).rollback()
        raise
    await (await get_db()).commit()


async def process_sub_to_lesson(lesson: Lesson, sub: Subscription | TLSubscription):
    try:
        if isinstance(sub, Subscription):
            await sub_to_individual_lesson(lesson, sub)
        elif isinstance(sub, TLSubscription):
            await sub_to_group_lesson(lesson, sub)
    except (LessonError, SubscriptionError):
        raise
    except Error:
        raise
