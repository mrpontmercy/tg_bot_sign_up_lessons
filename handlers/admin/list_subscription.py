import sqlite3
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    CALLBACK_DATA_GROUP_SUBSCRIPTION_PREFIX,
    CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION_PREFIX,
    CALLBACK_SUBSCRIPTION_PREFIX,
    SUB_GROUP_CODE,
    SUB_INDIVIDUAL_CODE,
)
from handlers.response import edit_callbackquery_template
from services.admin.kb import get_type_subscription_keyboard
from services.admin.list_subscription import (
    delete_group_subscription,
    delete_individual_subscription,
    get_available_group_subs,
    get_available_individual_subs,
)
from services.decorators import admin_required
from services.exceptions import SubscriptionError
from services.kb import get_back_keyboard, get_flip_delete_back_keyboard
from services.states import InterimAdminState, SwitchState
from services.utils import Subscription, TLSubscription


@admin_required
async def show_type_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    type_subs_kb = get_type_subscription_keyboard(SwitchState.RETURN_PREV_CONV)
    await query.edit_message_text(
        text="Выберите как тип абонементов хотите посмотреть!",
        reply_markup=type_subs_kb,
    )
    return SwitchState.CHOOSE_ACTION


@admin_required
async def list_available_individual_subs_admin(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    back_kb = get_back_keyboard(InterimAdminState.LIST_AVAILABLE_SUBS)
    try:
        subs: list[Subscription] = await get_available_individual_subs()
    except SubscriptionError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION

    switch_kb = get_flip_delete_back_keyboard(
        0,
        len(subs),
        CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION_PREFIX,
        str(InterimAdminState.LIST_AVAILABLE_SUBS),
    )
    sub = subs[0]
    context.user_data["sub_id"] = sub.id
    context.user_data["sub_type"] = SUB_INDIVIDUAL_CODE

    await edit_callbackquery_template(
        query,
        "subs.jinja",
        data={"sub_key": sub.sub_key, "num_of_classes": sub.num_of_classes},
        keyboard=switch_kb,
    )
    return SwitchState.CHOOSE_ACTION


@admin_required
async def list_individual_subs_button_admin(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    back_kb = get_back_keyboard(InterimAdminState.LIST_AVAILABLE_SUBS)
    try:
        subs = await get_available_individual_subs()
    except SubscriptionError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION
    current_index = int(query.data[len(CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION_PREFIX) :])
    sub = subs[current_index]
    context.user_data["sub_id"] = sub.id

    switch_kb = get_flip_delete_back_keyboard(
        current_index,
        len(subs),
        CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION_PREFIX,
        str(InterimAdminState.LIST_AVAILABLE_SUBS),
    )
    context.user_data["sub_type"] = SUB_INDIVIDUAL_CODE
    await edit_callbackquery_template(
        query,
        "subs.jinja",
        data={"sub_key": sub.sub_key, "num_of_classes": sub.num_of_classes},
        keyboard=switch_kb,
    )
    return SwitchState.CHOOSE_ACTION


@admin_required
async def list_available_group_subs_admin(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    back_kb = get_back_keyboard(InterimAdminState.LIST_AVAILABLE_SUBS)
    try:
        subs: list[TLSubscription] = await get_available_group_subs()
    except SubscriptionError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION

    switch_kb = get_flip_delete_back_keyboard(
        0,
        len(subs),
        CALLBACK_DATA_GROUP_SUBSCRIPTION_PREFIX,
        str(InterimAdminState.LIST_AVAILABLE_SUBS),
    )
    sub = subs[0]
    context.user_data["sub_id"] = sub.id
    context.user_data["sub_type"] = SUB_GROUP_CODE

    await edit_callbackquery_template(
        query,
        "group_subs.jinja",
        data={
            "sub_key": sub.sub_key,
            "num_of_classes": sub.num_of_classes,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
        },
        keyboard=switch_kb,
    )
    return SwitchState.CHOOSE_ACTION


@admin_required
async def list_group_subs_button_admin(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    back_kb = get_back_keyboard(InterimAdminState.LIST_AVAILABLE_SUBS)
    try:
        subs = await get_available_group_subs()
    except SubscriptionError as e:
        await edit_callbackquery_template(
            query, "error.jinja", err=str(e), keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION
    current_index = int(query.data[len(CALLBACK_DATA_GROUP_SUBSCRIPTION_PREFIX) :])
    sub = subs[current_index]
    context.user_data["sub_id"] = sub.id

    switch_kb = get_flip_delete_back_keyboard(
        current_index,
        len(subs),
        CALLBACK_DATA_GROUP_SUBSCRIPTION_PREFIX,
        str(InterimAdminState.LIST_AVAILABLE_SUBS),
    )
    context.user_data["sub_type"] = SUB_GROUP_CODE
    await edit_callbackquery_template(
        query,
        "group_subs.jinja",
        data={
            "sub_key": sub.sub_key,
            "num_of_classes": sub.num_of_classes,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
        },
        keyboard=switch_kb,
    )
    return SwitchState.CHOOSE_ACTION


@admin_required
async def remove_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sub_id: int | None = context.user_data.get("sub_id")
    sub_type = context.user_data.get("sub_type")
    back_kb = get_back_keyboard(SwitchState.RETURN_PREV_CONV)
    if sub_id is None or sub_type is None:
        await edit_callbackquery_template(
            query, "error.jinja", err="Не удалось найти подписку!", keyboard=back_kb
        )
        return SwitchState.CHOOSE_ACTION

    try:
        if sub_type == SUB_INDIVIDUAL_CODE:
            await delete_individual_subscription(sub_id)
        elif sub_type == SUB_GROUP_CODE:
            await delete_group_subscription(sub_id)
    except sqlite3.Error:
        await edit_callbackquery_template(
            query,
            "error.jinja",
            err="Не удалось удалить подписку! Обратитесь к администратору",
            keyboard=back_kb,
        )
        return SwitchState.CHOOSE_ACTION

    back_kb = get_back_keyboard(InterimAdminState.LIST_AVAILABLE_SUBS)
    await query.edit_message_text("Абонемент удален!", reply_markup=back_kb)
    return SwitchState.CHOOSE_ACTION
