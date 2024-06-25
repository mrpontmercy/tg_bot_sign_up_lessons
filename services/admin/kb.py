from config import (
    CALLBACK_DATA_GROUP_SUBSCRIPTION,
    CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION,
)
from services.states import END, InterimAdminState


from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                "Создать ключ",
                callback_data=str(InterimAdminState.START_GENERATE_SUB),
            ),
            InlineKeyboardButton(
                "Доступные ключи",
                callback_data=str(InterimAdminState.LIST_AVAILABLE_SUBS),
            ),
        ],
        [
            InlineKeyboardButton(
                "Обновить уроки",
                callback_data=str(InterimAdminState.START_UPDATE_LESSONS),
            ),
            InlineKeyboardButton(
                "Все уроки", callback_data=str(InterimAdminState.SHOW_ALL_LESSONS)
            ),
            InlineKeyboardButton(
                "Добавить преподователя",
                callback_data=str(InterimAdminState.ENTER_LECTURER_PHONE),
            ),
        ],
        [InlineKeyboardButton("Завершить", callback_data=str(END))],
    ]

    return InlineKeyboardMarkup(buttons)


def get_type_subscription_keyboard(back_button_state):
    buttons = [
        [
            InlineKeyboardButton(
                "Индивидуальная(Бессрочная)",
                callback_data=CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION,
            ),
        ],
        [
            InlineKeyboardButton(
                "Групповая(Временная)",
                callback_data=CALLBACK_DATA_GROUP_SUBSCRIPTION,
            )
        ],
        [InlineKeyboardButton("Назад", callback_data=str(back_button_state))],
    ]
    return InlineKeyboardMarkup(buttons)
