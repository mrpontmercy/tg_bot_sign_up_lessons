import os
from pathlib import Path
import dotenv

dotenv.load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")

SQLITE_DB_FILE = BASE_DIR / "db.sqlite3"
LESSONS_DIR = BASE_DIR / "course_files"
TEMPLATE_DIR = BASE_DIR / "templates"

CALLBACK_DATA_DELETESUBSCRIPTION = "deleteSub"
CALLBACK_DATA_SUBSCRIBE_TO_LESSON = "subscribeLesson"
CALLBACK_DATA_CANCEL_LESSON = "cancelLesson"
CALLBACK_DATA_EDIT_LESSON = "editLesson"
CALLBACK_DATA_DELETELESSON_ADMIN = "deleteLessonAdmin"

CALLBACK_SUB_PREFIX = "sub_"
CALLBACK_LESSON_PREFIX = "lesson_"
CALLBACK_USER_LESSON_PREFIX = "user_lesson_"


DATETIME_FORMAT = "%Y-%m-%d %H:%M"
LECTURER_STATUS = "Преподаватель"
ADMIN_STATUS = "Админ"
