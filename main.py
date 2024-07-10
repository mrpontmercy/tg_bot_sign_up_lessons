import logging

from telegram.ext import Application

from config import TELEGRAM_BOT_TOKEN
from db import close_db
from handlers.admin.init_admin_handler import ADMIN_CONV_HANDLER
from handlers.init_all_handlers import (
    START_CONV_HANLER,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

if TELEGRAM_BOT_TOKEN is None:
    raise ValueError(f"Не указан Telegram Token!")


def main():

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(START_CONV_HANLER)
    app.add_handler(ADMIN_CONV_HANDLER)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        logger.warning(traceback.format_exc())
    finally:
        close_db()
