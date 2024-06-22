from enum import Enum, auto
from telegram.ext import ConversationHandler


END = ConversationHandler.END


class InterimStartState(Enum):
    START_REGISTER = auto()
    START_ACTIVATE_SUBSCRIPTION = auto()
    BACK_TO_START = auto()


class StartState(Enum):
    SHOWING = auto()
    CHOOSE_ACTION = auto()
    ACTIVATE_SUBSCRIPTION = auto()
    REGISTRATION = auto()
    ACTIVETE_SUBSCRIPTION = auto()
