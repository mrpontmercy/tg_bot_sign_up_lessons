from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from services.states import END, InterimStartState


def get_non_register_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "Регистрация", callback_data=str(InterimStartState.START_REGISTER)
            ),
        ],
        [InlineKeyboardButton("Отменить", callback_data=str(END))],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_registred_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "Активировать абонемент",
                callback_data=str(InterimStartState.START_ACTIVATE_SUBSCRIPTION),
            ),
            InlineKeyboardButton(
                "Остаток абонемента", callback_data=str(InterimStartState.START_REGISTER)
            ),
        ],
        [
            InlineKeyboardButton(
                "Доступные занятия", callback_data=str(InterimStartState.START_REGISTER)
            ),
            InlineKeyboardButton(
                "Мои занятия", callback_data=str(InterimStartState.START_REGISTER)
            ),
        ],
        [InlineKeyboardButton("Отменить", callback_data=str(END))],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_back_kb(back_state):
    keyboard = [[InlineKeyboardButton("Назад", callback_data=str(back_state))]]

    return InlineKeyboardMarkup(keyboard)


def get_retry_or_back_keyboard(retry_state, end_state):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Попробовать снова", callback_data=str(retry_state)
                ),
                InlineKeyboardButton("Назад", callback_data=str(end_state)),
            ]
        ]
    )
    return keyboard
