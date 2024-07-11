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
    CALLBACK_DATA_GROUP_SUBSCRIPTION_PREFIX,
    CALLBACK_DATA_INDIVIDUAL_LESSON,
    CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX,
    CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION,
    CALLBACK_DATA_INDIVIDUAL_SUBSCRIPTION_PREFIX,
)
from handlers.admin.admin import admin_command, alert_user_admin, return_to_admin
from handlers.lessons.edit_lesson import (
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
from handlers.confirmation import CONFIRMATION_HANDLERS

from handlers.lessons.list_lessons import (
    all_group_lessons_button,
    all_individual_lessons_button,
    return_to_lessons,
    show_all_group_lessons,
    show_all_individual_lessons,
    start_show_lessons,
)
from handlers.lessons.upload_lessons import (
    insert_group_lessons_handler,
    insert_individual_lessons_handler,
    start_inserting_group_lessons,
    start_inserting_individual_lessons,
    start_inserting_lessons,
)
from handlers.start import stop
from services.decorators import admin_required
from services.states import (
    END,
    AdminState,
    EditLesson,
    InterimAdminState,
    InterimEditLesson,
    StopState,
    SwitchState,
    UploadLessonsState,
)

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
            admin_required(start_edit_lesson),
            pattern=f"^{InterimEditLesson.START_EDIT_LESSON}$",
        )
    ],
    states={
        EditLesson.CHOOSE_ACTION: EDIT_LESSON_CHOOSE_ACTION_HANDLERS,
        EditLesson.EDIT_TITLE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, admin_required(edit_title_lesson)
            )
        ],
        EditLesson.EDIT_TIMESTART: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, admin_required(edit_time_start_lesson)
            )
        ],
        EditLesson.EDIT_NUM_OF_SEATS: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, admin_required(edit_num_of_seats_lesson)
            )
        ],
        EditLesson.EDIT_LESSON_LINK: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, admin_required(edit_lesson_link)
            )
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            return_to_lessons, pattern=f"^{EditLesson.RETURN_PREV_CONV}$"
        )
    ],
    map_to_parent={StopState.STOPPING: SwitchState.CHOOSE_ACTION, END: END},
    allow_reentry=True,
)

LIST_ALL_LESSONS_CONV_HANDLER_ADMIN = ConversationHandler(
    [
        CallbackQueryHandler(
            start_show_lessons,
            pattern=f"^{SwitchState.START_SHOW_RESOURCES}$",
        )
    ],
    states={
        SwitchState.CHOOSE_ACTION: [
            CallbackQueryHandler(
                all_group_lessons_button,
                pattern="^" + CALLBACK_DATA_GROUP_LESSON_PREFIX + "\d+",
            ),
            CallbackQueryHandler(
                all_individual_lessons_button,
                pattern="^" + CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX + "\d+",
            ),
            CallbackQueryHandler(
                show_all_group_lessons,
                pattern=f"^{CALLBACK_DATA_GROUP_LESSON}$",
            ),
            CallbackQueryHandler(
                show_all_individual_lessons,
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

UPDATE_LESSONS_CONV_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            admin_required(start_inserting_lessons),
            pattern=f"^{UploadLessonsState.START_UPDATING_LESSONS}$",
        )
    ],
    states={
        UploadLessonsState.UPDATING_LESSONS: [
            CallbackQueryHandler(
                admin_required(start_inserting_group_lessons),
                pattern=f"^{CALLBACK_DATA_GROUP_LESSON}$",
            ),
            CallbackQueryHandler(
                admin_required(start_inserting_individual_lessons),
                pattern=f"^{CALLBACK_DATA_INDIVIDUAL_LESSON}$",
            ),
        ],
        UploadLessonsState.INSERT_INDIVIDUAL_LESSONS: [
            MessageHandler(
                filters.Document.MimeType("text/csv"),
                admin_required(insert_individual_lessons_handler),
            ),
        ],
        UploadLessonsState.INSERT_GROUP_LESSONS: [
            MessageHandler(
                filters.Document.MimeType("text/csv"),
                admin_required(insert_group_lessons_handler),
            ),
        ],
    },
    fallbacks=[
        CommandHandler("stop", stop),
        CallbackQueryHandler(
            admin_required(return_to_admin),
            pattern=f"^{UploadLessonsState.RETURN_PREV_CONV}$",
        ),
        CallbackQueryHandler(
            admin_required(start_inserting_lessons),
            pattern=f"^{UploadLessonsState.RETURN_BACK}$",
        ),
    ],
    map_to_parent={
        StopState.STOPPING: AdminState.CHOOSE_ACTION,
        END: END,
    },
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
    LIST_SUBS_CONV_HANDLER,
    LIST_ALL_LESSONS_CONV_HANDLER_ADMIN,
    UPDATE_LESSONS_CONV_HANDLER,
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
    },
    fallbacks=[
        CommandHandler("stop", stop),
        CallbackQueryHandler(stop, pattern=f"^{END}$"),
        CallbackQueryHandler(
            admin_command, pattern=f"^{InterimAdminState.BACK_TO_ADMIN}$"
        ),
        MessageHandler(filters.TEXT & filters.COMMAND, alert_user_admin),
    ],
)
