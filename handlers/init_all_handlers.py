from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import (
    CALLBACK_DATA_CANCEL_LESSON,
    CALLBACK_DATA_DELETELESSON_ADMIN,
    CALLBACK_DATA_DELETESUBSCRIPTION,
    CALLBACK_DATA_SUBSCRIBE_TO_LESSON,
    CALLBACK_LESSON_PREFIX,
    CALLBACK_SUB_PREFIX,
    CALLBACK_USER_LESSON_PREFIX,
)
from handlers.admin.admin import (
    admin_command,
    return_to_admin,
)
from handlers.admin.edit_lesson import (
    edit_num_of_seats_lesson,
    edit_time_start_lesson,
    edit_title_lesson,
    start_edit_lesson,
    start_edit_num_of_seats_lesson,
    start_edit_time_start_lesson,
    start_edit_title_lesson,
)
from handlers.admin.list_lessons import (
    all_lessons_button_admin,
    return_to_lessons_admin,
    show_all_lessons_admin,
)
from handlers.admin.list_subscription import (
    list_available_subs_admin,
    list_subs_button_admin,
)
from handlers.admin.make_lecturer import enter_lecturer_phone_number, make_lecturer
from handlers.admin.subscription import (
    make_new_subscription,
    start_generating_subscription,
)
from handlers.admin.upload_lessons import insert_lessons_handler, start_inserting_lessons
from handlers.confirmation import (
    cancel_action_button,
    confirm_action_button,
    confirmation_action_handler,
)
from handlers.user.lesson import available_lessons_button, show_available_lessons
from handlers.user.registration import start_registration, user_registration
from handlers.start import back_to_start, start_command, stop
from handlers.user.schedule_lesson import schedule_lessons_button, show_schedule_lessons
from handlers.user.subscription import (
    register_sub_key_to_user,
    show_number_of_remaining_classes_on_subscription,
    start_activating_subkey,
)
from services.states import (
    END,
    AdminState,
    EditLesson,
    InterimAdminState,
    InterimEditLesson,
    InterimStartState,
    StartState,
    SwitchState,
)

CQH_CONFIRM_SUBSCRIBE = CallbackQueryHandler(
    confirmation_action_handler,
    pattern=f".*({CALLBACK_DATA_DELETESUBSCRIPTION}|{CALLBACK_DATA_SUBSCRIBE_TO_LESSON}|{CALLBACK_DATA_CANCEL_LESSON}|{CALLBACK_DATA_DELETELESSON_ADMIN})$",
)

CQH_CONFIRM_SUBCRIBE_YES = CallbackQueryHandler(
    confirm_action_button, pattern=".*_confirm_action$"
)

CQH_CONFIRM_SUBCRIBE_CANCEL = CallbackQueryHandler(
    cancel_action_button, pattern=".*_cancel_action$"
)

AVAILABLE_LESSONS_CONV_HANDLER_USER = ConversationHandler(
    [
        CallbackQueryHandler(
            show_available_lessons,
            pattern=f"^{InterimStartState.SHOW_AVAILABLE_LESSONS}$",
        )
    ],
    states={
        SwitchState.CHOOSE_ACTION: [
            CallbackQueryHandler(
                available_lessons_button, pattern="^" + CALLBACK_LESSON_PREFIX + "\d+"
            )
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
            show_schedule_lessons, pattern=f"^{InterimStartState.SHOW_SCHEDULE_LESSONS}$"
        )
    ],
    states={
        SwitchState.CHOOSE_ACTION: [
            CallbackQueryHandler(
                schedule_lessons_button,
                pattern="^" + CALLBACK_USER_LESSON_PREFIX + "\d+",
            )
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
        show_number_of_remaining_classes_on_subscription,
        pattern=f"^{InterimStartState.SHOW_REMAINDER_SUBSCRIPTION}$",
    ),
    AVAILABLE_LESSONS_CONV_HANDLER_USER,
    SCHEDULE_LESSONS_CONV_HANDLER_USER,
]

START_CONV_HANLER = ConversationHandler(
    [CommandHandler("start", start_command)],
    states={
        StartState.CHOOSE_ACTION: START_CHOOSE_ACTION_HANDLERS,
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
    ],
)

LIST_SUBS_CONV_HANDLER = ConversationHandler(
    [
        CallbackQueryHandler(
            list_available_subs_admin,
            pattern=f"^{InterimAdminState.LIST_AVAILABLE_SUBS}$",
        )
    ],
    states={
        SwitchState.CHOOSE_ACTION: [
            CallbackQueryHandler(
                list_subs_button_admin, pattern="^" + CALLBACK_SUB_PREFIX + "\d+"
            )
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            return_to_admin, pattern=f"^{SwitchState.RETURN_PREV_CONV}$"
        )
    ],
    map_to_parent={END: AdminState.CHOOSE_ACTION},
    allow_reentry=True,
)


EDIT_LESSON_CHOOSE_ACTION_HANDLERS = [
    CallbackQueryHandler(
        start_edit_title_lesson, pattern=f"^{InterimEditLesson.START_EDIT_TITLE}$"
    ),
    CallbackQueryHandler(
        start_edit_time_start_lesson,
        pattern=f"^{InterimEditLesson.START_EDIT_TIMESTART}$",
    ),
    CallbackQueryHandler(
        start_edit_num_of_seats_lesson,
        pattern=f"^{InterimEditLesson.START_EDIT_NUM_OF_SEATS}$",
    ),
]

EDIT_LESSON_CONV_HANDLER_ADMIN = ConversationHandler(
    [
        CallbackQueryHandler(
            start_edit_lesson, pattern=f"^{InterimEditLesson.START_EDIT_LESSON}$"
        )
    ],
    states={
        EditLesson.CHOOSE_ACTION: EDIT_LESSON_CHOOSE_ACTION_HANDLERS,
        EditLesson.EDIT_TITLE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_title_lesson)
        ],
        EditLesson.EDIT_TIMESTART: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_time_start_lesson)
        ],
        EditLesson.EDIT_NUM_OF_SEATS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_num_of_seats_lesson)
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            return_to_lessons_admin, pattern=f"^{EditLesson.RETURN_PREV_CONV}$"
        )
    ],
    map_to_parent={END: SwitchState.CHOOSE_ACTION},
    allow_reentry=True,
)

LIST_ALL_LESSONS_CONV_HANDLER_ADMIN = ConversationHandler(
    [
        CallbackQueryHandler(
            show_all_lessons_admin, pattern=f"^{InterimAdminState.SHOW_ALL_LESSONS}$"
        )
    ],
    states={
        SwitchState.CHOOSE_ACTION: [
            CallbackQueryHandler(
                all_lessons_button_admin, pattern="^" + CALLBACK_LESSON_PREFIX + "\d+"
            ),
            EDIT_LESSON_CONV_HANDLER_ADMIN,
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            return_to_admin, pattern=f"^{SwitchState.RETURN_PREV_CONV}$"
        )
    ],
    map_to_parent={END: AdminState.CHOOSE_ACTION},
    allow_reentry=True,
)


ADMIN_CHOOSE_ACTION_HANDLERS = [
    CallbackQueryHandler(
        enter_lecturer_phone_number,
        pattern=f"^{InterimAdminState.ENTER_LECTURER_PHONE}$",
    ),
    CallbackQueryHandler(
        start_generating_subscription,
        pattern=f"^{InterimAdminState.START_GENERATE_SUB}$",
    ),
    CallbackQueryHandler(
        start_inserting_lessons, pattern=f"^{InterimAdminState.START_UPDATE_LESSONS}$"
    ),
    LIST_SUBS_CONV_HANDLER,
    LIST_ALL_LESSONS_CONV_HANDLER_ADMIN,
]


ADMIN_CONV_HANDLER = ConversationHandler(
    entry_points=[
        CommandHandler("admin", admin_command),
    ],
    states={
        AdminState.CHOOSE_ACTION: ADMIN_CHOOSE_ACTION_HANDLERS,
        AdminState.ADD_LECTURER: [
            MessageHandler(
                filters.TEXT & filters.Regex("^(?!\/stop$).+"),
                make_lecturer,
            )
        ],
        AdminState.GENERATE_SUB: [
            MessageHandler(
                filters.TEXT & filters.Regex("^(?!\/stop$).+"),
                make_new_subscription,
            )
        ],
        AdminState.INSERT_LESSONS: [
            MessageHandler(
                filters.Document.MimeType("text/csv"),
                insert_lessons_handler,
            ),
        ],
    },
    fallbacks=[
        CommandHandler("stop", stop),
        CallbackQueryHandler(stop, pattern=f"^{END}$"),
        CallbackQueryHandler(
            admin_command, pattern=f"^{InterimAdminState.BACK_TO_ADMIN}$"
        ),
    ],
)
