import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    CALLBACK_DATA_CANCEL_LESSON,
    CALLBACK_DATA_DELETESUBSCRIPTION,
    CALLBACK_DATA_SUBSCRIBE_TO_LESSON,
)
from handlers.admin.list_subscription import (
    list_available_subs_admin,
    remove_subscription,
)
from handlers.user.lesson import show_available_lessons, subscribe_to_lesson
from handlers.user.schedule_lesson import cancel_lesson, show_schedule_lessons
from services.kb import get_back_keyboard, get_confirmation_keyboard
from services.states import AdminState, InterimAdminState


async def confirmation_action_handler(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prefix = query.data.split("_")[-1]
    confirm_kb = get_confirmation_keyboard(prefix)
    await query.edit_message_text(
        "Вы действительно хотите выполнить это действие?", reply_markup=confirm_kb
    )


async def confirm_action_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # action_confirm_action
    action = query.data.split("_")[0]

    if action == CALLBACK_DATA_DELETESUBSCRIPTION:
        try:
            return await remove_subscription(update, context)
        except sqlite3.Error as e:
            logging.getLogger(__name__).exception(e)
            back_kb = get_back_keyboard(InterimAdminState.LIST_AVAILABLE_SUBS)
            await query.edit_message_text(
                "Не удалось удалить абонемент!", reply_markup=back_kb
            )
            return AdminState.CHOOSE_ACTION
    elif action == CALLBACK_DATA_SUBSCRIBE_TO_LESSON:
        return await subscribe_to_lesson(update, context)
    elif action == CALLBACK_DATA_CANCEL_LESSON:
        return await cancel_lesson(update, context)

    # if action == CALLBACK_DATA_SUBSCRIBE:
    #     await subscribe_to_lesson(update, context)
    #     # await show_lessons(update, context)
    # elif action == CALLBACK_DATA_CANCEL_LESSON:
    #     await cancel_lesson(update, context)
    #     # await show_my_lessons(update, context)
    # elif action == CALLBACK_DATA_CANCEL_LESSON_LECTURER:
    #     await cancel_lesson_by_lecturer(update, context)
    #     await show_lecturer_lessons(update, context)


async def cancel_action_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data.split("_")[0]
    if action == CALLBACK_DATA_DELETESUBSCRIPTION:
        await list_available_subs_admin(update, context)
    if action == CALLBACK_DATA_SUBSCRIBE_TO_LESSON:
        await show_available_lessons(update, context)
    elif action == CALLBACK_DATA_CANCEL_LESSON:
        await show_schedule_lessons(update, context)
