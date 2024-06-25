from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import (
    CALLBACK_DATA_CANCEL_LESSON,
    CALLBACK_DATA_DELETELESSON_ADMIN,
    CALLBACK_DATA_DELETESUBSCRIPTION,
    CALLBACK_DATA_GROUP_LESSON,
    CALLBACK_DATA_INDIVIDUAL_LESSON,
    CALLBACK_DATA_SUBSCRIBE_TO_LESSON,
)
from services.states import (
    EditLesson,
    InterimEditLesson,
)


def get_type_lesson_keyboard(back_button_state):
    buttons = [
        [
            InlineKeyboardButton(
                "Индивидуальные", callback_data=CALLBACK_DATA_INDIVIDUAL_LESSON
            ),
            InlineKeyboardButton("Групповые", callback_data=CALLBACK_DATA_GROUP_LESSON),
        ],
        [InlineKeyboardButton("Назад", callback_data=str(back_button_state))],
    ]
    return InlineKeyboardMarkup(buttons)


def get_edit_lesson_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                "Изменить заголовок",
                callback_data=str(InterimEditLesson.START_EDIT_TITLE),
            ),
            InlineKeyboardButton(
                "Изменить дату",
                callback_data=str(InterimEditLesson.START_EDIT_TIMESTART),
            ),
        ],
        [
            InlineKeyboardButton(
                "Изменить количество доступных мест",
                callback_data=str(InterimEditLesson.START_EDIT_NUM_OF_SEATS),
            ),
            InlineKeyboardButton(
                "Изменить ссылку на занятие",
                callback_data=str(InterimEditLesson.START_EDIT_LESSON_LINK),
            ),
        ],
        [
            InlineKeyboardButton(
                "Завершить", callback_data=str(EditLesson.RETURN_PREV_CONV)
            )
        ],
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
                "Изменить", callback_data=f"{InterimEditLesson.START_EDIT_LESSON}"
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
