from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from services.states import END, SwitchState, UploadLessonsState


def get_lecturer_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                "Ваши занятия",
                callback_data=str(SwitchState.START_SHOW_RESOURCES),
            ),
            InlineKeyboardButton(
                "Добавить занятия",
                callback_data=str(UploadLessonsState.START_UPDATING_LESSONS),
            ),
        ],
        [InlineKeyboardButton("Завершить", callback_data=str(END))],
    ]

    return InlineKeyboardMarkup(buttons)
