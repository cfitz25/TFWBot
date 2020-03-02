from enum import Enum

class state_create_reply(Enum):
    NONE = 0
    BEGIN = 1
    ACTIONS_ADD = 2
    ACTIONS_REMOVE = 3
    REPLY_ADD = 4
    REPLY_REMOVE = 5
    END = 6
class enum_chat_types(Enum):
    UNKNOWN = 0
    PRIVATE = 1
    SUPERGROUP = 2
class message_types(Enum):
    UNKNOWN = 0
    TEXT = 1
    STICKER = 2
    GIF = 3