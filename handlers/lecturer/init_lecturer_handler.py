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
    CALLBACK_DATA_INDIVIDUAL_LESSON,
    CALLBACK_DATA_INDIVIDUAL_LESSON_PREFIX,
)
from handlers.confirmation import CONFIRMATION_HANDLERS
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
from handlers.lecturer.lecturer_start_command import lecturer_command, return_to_lecturer
from handlers.start import stop
from services.states import (
    END,
    EditLesson,
    InterimEditLesson,
    LecturerState,
    StopState,
    SwitchState,
    UploadLessonsState,
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
            start_edit_lesson,
            pattern=f"^{InterimEditLesson.START_EDIT_LESSON}$",
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
            return_to_lessons, pattern=f"^{EditLesson.RETURN_PREV_CONV}$"
        )
    ],
    map_to_parent={StopState.STOPPING: SwitchState.CHOOSE_ACTION, END: END},
    allow_reentry=True,
)


LIST_ALL_LESSONS_CONV_HANDLER = ConversationHandler(
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
            return_to_lecturer, pattern=f"^{SwitchState.RETURN_PREV_CONV}$"
        )
    ],
    map_to_parent={StopState.STOPPING: LecturerState.CHOOSE_ACTION, END: END},
    allow_reentry=True,
)

UPDATE_LESSONS_CONV_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            start_inserting_lessons,
            pattern=f"^{UploadLessonsState.START_UPDATING_LESSONS}$",
        )
    ],
    states={
        UploadLessonsState.UPDATING_LESSONS: [
            CallbackQueryHandler(
                start_inserting_group_lessons,
                pattern=f"^{CALLBACK_DATA_GROUP_LESSON}$",
            ),
            CallbackQueryHandler(
                start_inserting_individual_lessons,
                pattern=f"^{CALLBACK_DATA_INDIVIDUAL_LESSON}$",
            ),
        ],
        UploadLessonsState.INSERT_INDIVIDUAL_LESSONS: [
            MessageHandler(
                filters.Document.MimeType("text/csv"),
                insert_individual_lessons_handler,
            ),
        ],
        UploadLessonsState.INSERT_GROUP_LESSONS: [
            MessageHandler(
                filters.Document.MimeType("text/csv"),
                insert_group_lessons_handler,
            ),
        ],
    },
    fallbacks=[
        CommandHandler("stop", stop),
        CallbackQueryHandler(
            return_to_lecturer,
            pattern=f"^{UploadLessonsState.RETURN_PREV_CONV}$",
        ),
        CallbackQueryHandler(
            start_inserting_lessons,
            pattern=f"^{UploadLessonsState.RETURN_BACK}$",
        ),
    ],
    map_to_parent={
        StopState.STOPPING: LecturerState.CHOOSE_ACTION,
        END: END,
    },
)

LECTURER_CHOOSE_ACTION_HANDLERS = [
    LIST_ALL_LESSONS_CONV_HANDLER,
    UPDATE_LESSONS_CONV_HANDLER,
]

LECTURER_CONV_HANDLER = ConversationHandler(
    entry_points=[
        CommandHandler(command=["lecturer"], callback=lecturer_command),
    ],
    states={
        LecturerState.CHOOSE_ACTION: LECTURER_CHOOSE_ACTION_HANDLERS,
    },
    fallbacks=[
        CommandHandler("stop", stop),
        CallbackQueryHandler(stop, pattern=f"^{END}$"),
    ],
)
