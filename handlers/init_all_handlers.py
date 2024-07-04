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
    CALLBACK_DATA_GROUP_LESSON,
    CALLBACK_DATA_GROUP_LESSON_PREFIX,
    CALLBACK_DATA_GROUP_SUBSCRIPTION,
    CALLBACK_DATA_GROUP_SUBSCRIPTION_PREFIX,
    CALLBACK_DATA_INDIVIDUAL_LESSON,
    CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX,
    CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION,
    CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION_PREFIX,
    CALLBACK_DATA_SUBSCRIBE_TO_LESSON,
)
from handlers.admin.admin import (
    admin_command,
    alert_user_admin,
    return_to_admin,
)
from handlers.admin.edit_lesson import (
    edit_lesson_link,
    edit_num_of_seats_lesson,
    edit_time_start_lesson,
    edit_title_lesson,
    start_edit_lesson,
    start_edit_lesson_link_lesson,
    start_edit_num_of_seats_lesson,
    start_edit_time_start_lesson,
    start_edit_title_lesson,
)
from handlers.admin.list_lessons import (
    all_group_lessons_button_admin,
    all_individual_lessons_button_admin,
    return_to_lessons_admin,
    show_all_group_lessons_admin,
    show_all_individual_lessons_admin,
    start_show_lessons_admin,
)
from handlers.admin.list_subscription import (
    list_available_group_subs_admin,
    list_available_individual_subs_admin,
    list_group_subs_button_admin,
    list_individual_subs_button_admin,
    show_type_subscription,
)
from handlers.admin.make_lecturer import enter_lecturer_phone_number, make_lecturer
from handlers.admin.subscription import (
    make_new_group_subscription,
    make_new_individual_subscription,
    start_generating_group_subscription,
    start_generating_individual_subscription,
    start_generating_subscription,
)
from handlers.admin.upload_lessons import (
    insert_group_lessons_handler,
    insert_individual_lessons_handler,
    start_inserting_group_lessons,
    start_inserting_individual_lessons,
    start_inserting_lessons,
)
from handlers.confirmation import (
    cancel_action_button,
    confirm_action_button,
    confirmation_action_handler,
)
from handlers.user.lesson import (
    available_group_lessons_button,
    available_individual_lessons_button,
    show_available_group_lessons,
    show_available_individual_lessons,
    start_show_lessons,
)
from handlers.user.registration import start_registration, user_registration
from handlers.start import alert_user_start, back_to_start, start_command, stop
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
    AdminState,
    EditLesson,
    InterimAdminState,
    InterimEditLesson,
    InterimStartState,
    StartState,
    StopState,
    SwitchState,
)


CQH_CONFIRM_SUBSCRIBE = CallbackQueryHandler(
    confirmation_action_handler,
    pattern=(
        f".*({CALLBACK_DATA_DELETESUBSCRIPTION}|{CALLBACK_DATA_SUBSCRIBE_TO_LESSON}|"
        f"{CALLBACK_DATA_CANCEL_LESSON}|{CALLBACK_DATA_DELETELESSON_ADMIN})$"
    ),
)

CQH_CONFIRM_SUBCRIBE_YES = CallbackQueryHandler(
    confirm_action_button, pattern=".*_confirm_action$"
)

CQH_CONFIRM_SUBCRIBE_CANCEL = CallbackQueryHandler(
    cancel_action_button, pattern=".*_cancel_action$"
)

CONFIRMATION_HANDLERS = [
    CQH_CONFIRM_SUBSCRIBE,
    CQH_CONFIRM_SUBCRIBE_YES,
    CQH_CONFIRM_SUBCRIBE_CANCEL,
]


LIST_SUBS_CONV_HANDLER = ConversationHandler(
    [
        CallbackQueryHandler(
            show_type_subscription,
            pattern=f"^{InterimAdminState.LIST_AVAILABLE_SUBS}$",
        )
    ],
    states={
        SwitchState.CHOOSE_ACTION: [
            CallbackQueryHandler(
                list_available_individual_subs_admin,
                pattern=f"^{CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION}$",
            ),
            CallbackQueryHandler(
                list_available_group_subs_admin,
                pattern=f"^{CALLBACK_DATA_GROUP_SUBSCRIPTION}$",
            ),
            CallbackQueryHandler(
                list_individual_subs_button_admin,
                pattern="^" + CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION_PREFIX + "\d+",
            ),
            CallbackQueryHandler(
                list_group_subs_button_admin,
                pattern="^" + CALLBACK_DATA_GROUP_SUBSCRIPTION_PREFIX + "\d+",
            ),
            *CONFIRMATION_HANDLERS,
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            return_to_admin, pattern=f"^{SwitchState.RETURN_PREV_CONV}$"
        )
    ],
    map_to_parent={StopState.STOPPING: AdminState.CHOOSE_ACTION, END: END},
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
    CallbackQueryHandler(
        start_edit_lesson_link_lesson,
        pattern=f"^{InterimEditLesson.START_EDIT_LESSON_LINK}$",
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
        EditLesson.EDIT_LESSON_LINK: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_lesson_link)
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            return_to_lessons_admin, pattern=f"^{EditLesson.RETURN_PREV_CONV}$"
        )
    ],
    map_to_parent={StopState.STOPPING: SwitchState.CHOOSE_ACTION, END: END},
    allow_reentry=True,
)

LIST_ALL_LESSONS_CONV_HANDLER_ADMIN = ConversationHandler(
    [
        CallbackQueryHandler(
            start_show_lessons_admin,
            pattern=f"^{InterimAdminState.SHOW_ALL_LESSONS}$",
        )
    ],
    states={
        SwitchState.CHOOSE_ACTION: [
            CallbackQueryHandler(
                all_group_lessons_button_admin,
                pattern="^" + CALLBACK_DATA_GROUP_LESSON_PREFIX + "\d+",
            ),
            CallbackQueryHandler(
                all_individual_lessons_button_admin,
                pattern="^" + CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX + "\d+",
            ),
            CallbackQueryHandler(
                show_all_group_lessons_admin,
                pattern=f"^{CALLBACK_DATA_GROUP_LESSON}$",
            ),
            CallbackQueryHandler(
                show_all_individual_lessons_admin,
                pattern=f"^{CALLBACK_DATA_INDIVIDUAL_LESSON}$",
            ),
            EDIT_LESSON_CONV_HANDLER_ADMIN,
            *CONFIRMATION_HANDLERS,
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            return_to_admin, pattern=f"^{SwitchState.RETURN_PREV_CONV}$"
        )
    ],
    map_to_parent={StopState.STOPPING: AdminState.CHOOSE_ACTION, END: END},
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
        start_inserting_lessons,
        pattern=f"^{InterimAdminState.START_UPDATE_LESSONS}$",
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
        AdminState.GENERATING_SUBSCRIPTION: [
            CallbackQueryHandler(
                start_generating_individual_subscription,
                pattern=f"^{CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION}$",
            ),
            CallbackQueryHandler(
                start_generating_group_subscription,
                pattern=f"^{CALLBACK_DATA_GROUP_SUBSCRIPTION}$",
            ),
        ],
        AdminState.UPDATING_LESSONS: [
            CallbackQueryHandler(
                start_inserting_group_lessons, pattern=f"^{CALLBACK_DATA_GROUP_LESSON}$"
            ),
            CallbackQueryHandler(
                start_inserting_individual_lessons,
                pattern=f"^{CALLBACK_DATA_INDIVIDUAL_LESSON}$",
            ),
        ],
        AdminState.ADD_LECTURER: [
            MessageHandler(
                filters.TEXT & filters.Regex("^(?!\/stop$).+"),
                make_lecturer,
            )
        ],
        AdminState.GENERATE_INDIVIDUAL_SUB: [
            MessageHandler(
                filters.TEXT & filters.Regex("^(?!\/stop$).+"),
                make_new_individual_subscription,
            )
        ],
        AdminState.GENERATE_GROUP_SUB: [
            MessageHandler(
                filters.TEXT & filters.Regex("^(?!\/stop$).+"),
                make_new_group_subscription,
            )
        ],
        AdminState.INSERT_GROUP_LESSONS: [
            MessageHandler(
                filters.Document.MimeType("text/csv"),
                insert_group_lessons_handler,
            ),
        ],
        AdminState.INSERT_INDIVIDUAL_LESSONS: [
            MessageHandler(
                filters.Document.MimeType("text/csv"),
                insert_individual_lessons_handler,
            ),
        ],
    },
    fallbacks=[
        CommandHandler("stop", stop),
        CallbackQueryHandler(stop, pattern=f"^{END}$"),
        CallbackQueryHandler(
            admin_command, pattern=f"^{InterimAdminState.BACK_TO_ADMIN}$"
        ),
        MessageHandler(filters.TEXT, alert_user_admin),
    ],
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
