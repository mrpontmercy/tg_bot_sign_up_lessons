from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from services.states import END, InterimAdminState, SwitchState, UploadLessonsState


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
                callback_data=str(UploadLessonsState.START_UPDATING_LESSONS),
            ),
            InlineKeyboardButton(
                "Все уроки", callback_data=str(SwitchState.START_SHOW_RESOURCES)
            ),
            InlineKeyboardButton(
                "Добавить преподователя",
                callback_data=str(InterimAdminState.ENTER_LECTURER_PHONE),
            ),
        ],
        [InlineKeyboardButton("Завершить", callback_data=str(END))],
    ]

    return InlineKeyboardMarkup(buttons)
