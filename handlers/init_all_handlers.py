from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import (
    CALLBACK_DATA_GROUP_LESSON,
    CALLBACK_DATA_GROUP_LESSON_PREFIX,
    CALLBACK_DATA_GROUP_SUBSCRIPTION,
    CALLBACK_DATA_INDIVIDUAL_LESSON,
    CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX,
    CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION,
)
from handlers.confirmation import (
    CONFIRMATION_HANDLERS,
)
from handlers.start import alert_user_start, back_to_start, start_command, stop
from handlers.user.lesson import (
    available_group_lessons_button,
    available_individual_lessons_button,
    show_available_group_lessons,
    show_available_individual_lessons,
    start_show_lessons,
)
from handlers.user.registration import start_registration, user_registration
from handlers.user.schedule_lesson import (
    schedule_group_lessons_button,
    schedule_individual_lessons_button,
    show_schedule_group_lessons,
    show_schedule_individual_lessons,
    start_show_schedule_lessons,
)
from handlers.user.subscription import (
    register_sub_key_to_user,
    show_remainder_of_group_subscription,
    show_remainder_of_individual_subscription,
    show_remainder_of_subscription,
    start_activating_subkey,
)
from services.states import (
    END,
    InterimStartState,
    StartState,
    SwitchState,
)

AVAILABLE_LESSONS_CONV_HANDLER_USER = ConversationHandler(
    [
        CallbackQueryHandler(
            start_show_lessons,
            pattern=f"^{InterimStartState.SHOW_AVAILABLE_LESSONS}$",
        )
    ],
    states={
        SwitchState.CHOOSE_ACTION: [
            CallbackQueryHandler(
                show_available_group_lessons,
                pattern=f"^{CALLBACK_DATA_GROUP_LESSON}$",
            ),
            CallbackQueryHandler(
                show_available_individual_lessons,
                pattern=f"^{CALLBACK_DATA_INDIVIDUAL_LESSON}$",
            ),
            CallbackQueryHandler(
                available_group_lessons_button,
                pattern="^" + CALLBACK_DATA_GROUP_LESSON_PREFIX + "\d+",
            ),
            CallbackQueryHandler(
                available_individual_lessons_button,
                pattern="^" + CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX + "\d+",
            ),
            *CONFIRMATION_HANDLERS,
        ]
    },
    fallbacks=[
        CallbackQueryHandler(back_to_start, pattern=f"^{SwitchState.RETURN_PREV_CONV}$")
    ],
    map_to_parent={END: StartState.CHOOSE_ACTION},
    allow_reentry=True,
)

SCHEDULE_LESSONS_CONV_HANDLER_USER = ConversationHandler(
    [
        CallbackQueryHandler(
            start_show_schedule_lessons,
            pattern=f"^{InterimStartState.SHOW_SCHEDULE_LESSONS}$",
        )
    ],
    states={
        SwitchState.CHOOSE_ACTION: [
            CallbackQueryHandler(
                show_schedule_group_lessons,
                pattern=f"^{CALLBACK_DATA_GROUP_LESSON}$",
            ),
            CallbackQueryHandler(
                show_schedule_individual_lessons,
                pattern=f"^{CALLBACK_DATA_INDIVIDUAL_LESSON}$",
            ),
            CallbackQueryHandler(
                schedule_group_lessons_button,
                pattern="^" + CALLBACK_DATA_GROUP_LESSON_PREFIX + "\d+",
            ),
            CallbackQueryHandler(
                schedule_individual_lessons_button,
                pattern="^" + CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX + "\d+",
            ),
            *CONFIRMATION_HANDLERS,
        ]
    },
    fallbacks=[
        CallbackQueryHandler(back_to_start, pattern=f"^{SwitchState.RETURN_PREV_CONV}$")
    ],
    map_to_parent={END: StartState.CHOOSE_ACTION},
    allow_reentry=True,
)


START_CHOOSE_ACTION_HANDLERS = [
    CallbackQueryHandler(
        start_registration, pattern=f"^{InterimStartState.START_REGISTER}$"
    ),
    CallbackQueryHandler(
        start_activating_subkey,
        pattern=f"^{InterimStartState.START_ACTIVATE_SUBSCRIPTION}$",
    ),
    CallbackQueryHandler(
        show_remainder_of_subscription,
        pattern=f"^{InterimStartState.SHOW_REMAINDER_SUBSCRIPTION}$",
    ),
    AVAILABLE_LESSONS_CONV_HANDLER_USER,
    SCHEDULE_LESSONS_CONV_HANDLER_USER,
]

START_CONV_HANLER = ConversationHandler(
    [CommandHandler("start", start_command)],
    states={
        StartState.CHOOSE_ACTION: START_CHOOSE_ACTION_HANDLERS,
        StartState.CHOOSE_SUBSCRIPTION: [
            CallbackQueryHandler(
                show_remainder_of_individual_subscription,
                pattern=f"^{CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION}$",
            ),
            CallbackQueryHandler(
                show_remainder_of_group_subscription,
                pattern=f"^{CALLBACK_DATA_GROUP_SUBSCRIPTION}$",
            ),
        ],
        StartState.REGISTRATION: [
            MessageHandler(
                filters.TEXT & filters.Regex("^(?!\/stop$).+"),
                user_registration,
            ),
        ],
        StartState.ACTIVATE_SUBSCRIPTION: [
            MessageHandler(
                filters.TEXT & filters.Regex("^(?!\/stop$).+"),
                register_sub_key_to_user,
            ),
        ],
    },
    fallbacks=[
        CommandHandler("stop", stop),
        CallbackQueryHandler(
            start_command, pattern=f"^{InterimStartState.BACK_TO_START}$"
        ),
        CallbackQueryHandler(stop, pattern=f"^{END}$"),
        MessageHandler(filters.TEXT, alert_user_start),
    ],
)
