from dataclasses import dataclass


@dataclass
class EnvSettings:
    TELEGRAM_BOT_TOKEN: str
    MY_PERSONAL_ID: int
    API_ID: int
    API_HASH: str
    WHO_SEND: list[str | int]
    TIME_TO_WAIT: int
    TIME_TO_WAIT_BETWEEN_SEND: int