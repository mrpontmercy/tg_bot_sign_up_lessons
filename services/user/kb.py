from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from services.db import get_user_by_tg_id
from services.exceptions import UserError
from services.states import END, InterimStartState


def get_non_register_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                "Регистрация", callback_data=str(InterimStartState.START_REGISTER)
            ),
        ],
        [InlineKeyboardButton("Завершить", callback_data=str(END))],
    ]

    return InlineKeyboardMarkup(buttons)


def get_registred_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                "Активировать абонемент",
                callback_data=str(InterimStartState.START_ACTIVATE_SUBSCRIPTION),
            ),
            InlineKeyboardButton(
                "Остаток абонемента",
                callback_data=str(InterimStartState.SHOW_REMAINDER_SUBSCRIPTION),
            ),
        ],
        [
            InlineKeyboardButton(
                "Доступные занятия",
                callback_data=str(InterimStartState.SHOW_AVAILABLE_LESSONS),
            ),
            InlineKeyboardButton(
                "Мои занятия", callback_data=str(InterimStartState.SHOW_SCHEDULE_LESSONS)
            ),
        ],
        [InlineKeyboardButton("Завершить", callback_data=str(END))],
    ]

    return InlineKeyboardMarkup(buttons)


async def get_current_user_keyboard(update: Update):
    """
    Получение клавиатуры, которая соответствует данному пользователю
    """
    user_tg_id = update.effective_user.id
    kb = None
    try:
        await get_user_by_tg_id(user_tg_id)
    except UserError as e:
        kb = get_non_register_keyboard()
    else:
        kb = get_registred_keyboard()

    return kb
