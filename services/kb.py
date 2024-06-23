from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import (
    CALLBACK_DATA_CANCEL_LESSON,
    CALLBACK_DATA_DELETELESSON_ADMIN,
    CALLBACK_DATA_DELETESUBSCRIPTION,
    CALLBACK_DATA_EDIT_LESSON,
    CALLBACK_DATA_SUBSCRIBE_TO_LESSON,
)
from services.states import END, AdminState, InterimAdminState, InterimStartState


def get_non_register_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                "Регистрация", callback_data=str(InterimStartState.START_REGISTER)
            ),
        ],
        [InlineKeyboardButton("Отменить", callback_data=str(END))],
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
        [InlineKeyboardButton("Отменить", callback_data=str(END))],
    ]

    return InlineKeyboardMarkup(buttons)


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
        [InlineKeyboardButton("Назад", callback_data=str(END))],
    ]

    return InlineKeyboardMarkup(buttons)


def get_confirmation_keyboard(prefix):
    buttons = [
        [
            InlineKeyboardButton(
                "Подтвердить", callback_data=f"{prefix}_confirm_action"
            ),
            InlineKeyboardButton("Отменить", callback_data=f"{prefix}_cancel_action"),
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_back_keyboard(back_state):
    buttons = [[InlineKeyboardButton("Назад", callback_data=str(back_state))]]

    return InlineKeyboardMarkup(buttons)


def get_retry_or_back_keyboard(retry_state, end_state):
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Попробовать снова", callback_data=str(retry_state)
                ),
                InlineKeyboardButton("Назад", callback_data=str(end_state)),
            ]
        ]
    )
    return buttons


def get_flip_edit_delete_back_keyboard(
    current_index, number_of_items, prefix, back_button_callback: str
):
    keyboard = _get_flip_buttons(current_index, number_of_items, prefix)
    keyboard.append(
        [
            InlineKeyboardButton(
                "Изменить", callback_data=f"{prefix}{CALLBACK_DATA_EDIT_LESSON}"
            ),
            InlineKeyboardButton(
                "Удалить", callback_data=f"{prefix}{CALLBACK_DATA_DELETELESSON_ADMIN}"
            ),
        ]
    )
    keyboard.append(
        [InlineKeyboardButton(text="Назад", callback_data=back_button_callback)]
    )
    return InlineKeyboardMarkup(keyboard)


def get_flip_delete_back_keyboard(
    current_index, number_of_items, prefix, back_button_callback: str
):
    keyboard = _get_flip_buttons(current_index, number_of_items, prefix)
    keyboard.append(
        [
            InlineKeyboardButton(
                "Удалить", callback_data=f"{prefix}{CALLBACK_DATA_DELETESUBSCRIPTION}"
            )
        ]
    )
    keyboard.append(
        [InlineKeyboardButton(text="Назад", callback_data=back_button_callback)]
    )
    return InlineKeyboardMarkup(keyboard)


def get_flip_cancel_back_keyboard(
    current_index, number_of_items, prefix, back_button_callback: str
):
    keyboard = _get_flip_buttons(current_index, number_of_items, prefix)
    keyboard.append(
        [
            InlineKeyboardButton(
                "Отменить", callback_data=f"{prefix}{CALLBACK_DATA_CANCEL_LESSON}"
            )
        ]
    )
    keyboard.append(
        [InlineKeyboardButton(text="Назад", callback_data=back_button_callback)]
    )
    return InlineKeyboardMarkup(keyboard)


def get_flip_signup_back_keyboard(
    current_index, number_of_items, prefix, back_button_callback: str
):
    keyboard = _get_flip_buttons(current_index, number_of_items, prefix)
    keyboard.append(
        [
            InlineKeyboardButton(
                "Записаться",
                callback_data=f"{prefix}{CALLBACK_DATA_SUBSCRIBE_TO_LESSON}",
            )
        ]
    )
    keyboard.append(
        [InlineKeyboardButton(text="Назад", callback_data=back_button_callback)]
    )
    return InlineKeyboardMarkup(keyboard)


def _get_flip_buttons(current_index, number_of_items, prefix):
    prev_ind = current_index - 1
    if prev_ind < 0:
        prev_ind = number_of_items - 1

    next_ind = current_index + 1
    if next_ind > number_of_items - 1:
        next_ind = 0

    buttons = [
        [
            InlineKeyboardButton("<", callback_data=f"{prefix}{prev_ind}"),
            InlineKeyboardButton(
                f"{current_index + 1} / {number_of_items}", callback_data=" "
            ),
            InlineKeyboardButton(">", callback_data=f"{prefix}{next_ind}"),
        ],
    ]
    return buttons
