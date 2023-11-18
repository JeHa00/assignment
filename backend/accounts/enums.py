from enum import StrEnum, auto


class UserInformation(StrEnum):
    user_id = auto()
    username = auto()
    password = auto()


class TokenInformation(StrEnum):
    token = auto()
    access_token = auto()
    refresh_token = auto()
