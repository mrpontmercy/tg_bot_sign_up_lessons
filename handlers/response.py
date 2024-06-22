from telegram import CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from services.templates import render_template


async def send_template_message(
    tg_id: int,
    template_name: str,
    *,
    context: ContextTypes.DEFAULT_TYPE,
    keyboard: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None,
    data: dict | None = None,
    replace: bool = True,
):
    await context.bot.send_message(
        tg_id,
        render_template(template_name, data=data, replace=replace),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


async def edit_callbackquery_template(
    query: CallbackQuery,
    template_name: str,
    *,
    err: str | None = None,
    keyboard: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None,
    data: dict | None = None,
    replace: bool = True,
):
    await query.edit_message_text(
        render_template(template_name, err=err, data=data, replace=replace),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


async def send_error_message(
    user_tg_id: int,
    context: ContextTypes.DEFAULT_TYPE,
    data: dict | None = None,
    err: str | None = None,
    keyboard: InlineKeyboardMarkup | None = None,
):
    await context.bot.send_message(
        user_tg_id,
        render_template("error.jinja", err=err, data=data),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )
