import logging
import sqlite3

from telegram import Update
from telegram.ext import ContextTypes

from config import (
    CALLBACK_DATA_CANCEL_LESSON,
    CALLBACK_DATA_DELETELESSON_ADMIN,
    CALLBACK_DATA_DELETESUBSCRIPTION,
    CALLBACK_DATA_SUBSCRIBE_TO_LESSON,
    SUB_GROUP_CODE,
    SUB_INDIVIDUAL_CODE,
)
from handlers.admin.list_lessons import (
    delete_lesson_admin,
    show_all_group_lessons_admin,
    show_all_individual_lessons_admin,
)
from handlers.admin.list_subscription import (
    list_available_group_subs_admin,
    list_available_individual_subs_admin,
    remove_subscription,
)
from handlers.user.lesson import (
    show_available_group_lessons,
    show_available_individual_lessons,
    subscribe_to_lesson,
)
from handlers.user.schedule_lesson import (
    cancel_lesson,
    show_schedule_group_lessons,
    show_schedule_individual_lessons,
)
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
    elif action == CALLBACK_DATA_DELETELESSON_ADMIN:
        return await delete_lesson_admin(update, context)

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
        sub_type = context.user_data.get("sub_type")
        if sub_type == SUB_INDIVIDUAL_CODE:
            await list_available_individual_subs_admin(update, context)
        elif sub_type == SUB_GROUP_CODE:
            await list_available_group_subs_admin(update, context)
    if action == CALLBACK_DATA_SUBSCRIBE_TO_LESSON:
        lesson = context.user_data.get("curr_lesson")
        if lesson.is_group:
            await show_available_group_lessons(update, context)
        else:
            await show_available_individual_lessons(update, context)
    elif action == CALLBACK_DATA_CANCEL_LESSON:
        lesson = context.user_data.get("curr_lesson")
        if lesson.is_group:
            await show_schedule_group_lessons(update, context)
        else:
            await show_schedule_individual_lessons(update, context)
    elif action == CALLBACK_DATA_DELETELESSON_ADMIN:
        lesson = context.user_data.get("curr_lesson")
        if lesson.is_group:
            await show_all_group_lessons_admin(update, context)
        else:
            await show_all_individual_lessons_admin(update, context)
