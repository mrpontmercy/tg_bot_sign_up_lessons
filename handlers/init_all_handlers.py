from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from handlers.registration.registration import start_registration, user_registration
from handlers.start import back_to_start, start_command, stop
from handlers.subsription.subscription import start_activating_subkey
from services.states import END, InterimStartState, StartState


START_CHOOSE_ACTION_HANDLERS = [
    CallbackQueryHandler(
        start_registration, pattern=f"^{InterimStartState.START_REGISTER}$"
    ),
    CallbackQueryHandler(
        start_activating_subkey,
        pattern=f"^{InterimStartState.START_ACTIVATE_SUBSCRIPTION}$",
    ),
]

START_SHOWING_HANLERS = [
    CallbackQueryHandler(back_to_start, pattern=f"{END}"),
    CallbackQueryHandler(
        start_registration, pattern=f"^{InterimStartState.START_REGISTER}$"
    ),
    CallbackQueryHandler(
        start_activating_subkey,
        pattern=f"^{InterimStartState.START_ACTIVATE_SUBSCRIPTION}$",
    ),
]

START_CONV_HANLER = ConversationHandler(
    [CommandHandler("start", start_command)],
    states={
        StartState.SHOWING: START_SHOWING_HANLERS,
        StartState.CHOOSE_ACTION: START_CHOOSE_ACTION_HANDLERS,
        StartState.REGISTRATION: [
            MessageHandler(
                filters.TEXT & filters.Regex("^(?!\/stop$).+"),
                user_registration,
            ),
        ],
    },
    fallbacks=[
        CommandHandler("stop", stop),
        CallbackQueryHandler(
            start_command, pattern=f"^{InterimStartState.BACK_TO_START}$"
        ),
    ],
)

ADMIN_CONV_HANDLER = ConversationHandler()
