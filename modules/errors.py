from dotenv import load_dotenv
from os import getenv
from sys import exit


load_dotenv(verbose=True)

class ErrorOccurred(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.MESSAGE = message


class ErrorIdHashChats(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def check_main_errors() -> tuple[str, int, int, str, list[int | str | list[str | int]], int, int]:
    telegram_bot_token: str = getenv("TELEGRAM_BOT_TOKEN", "")
    personal_id_chat: int = int(getenv("MY_PERSONAL_ID", "0"))
    api_id: int = int(getenv("API_ID", "0"))
    api_hash: str = getenv("API_HASH", "")
    who_send: list[str | int | list[int | str]] = [
        int(item) if item[1:].isnumeric()
        else item.split("/") if "@" in item and "/" in item
        else list(map(int, item.split("/"))) if "/" in item
        else item
        for item in getenv("WHO_SEND", "").split(",")
    ]
    time_to_wait: int = int(getenv("TIME_TO_WAIT", 30))
    time_to_wait_between_send: int = int(getenv("TIME_TO_WAIT_BETWEEN_SEND", 1800))

    mistakes: dict[bool, str] = {
        not telegram_bot_token: "There is no TELEGRAM_BOT_TOKEN option in .env-file!",
        not personal_id_chat: "There is no MY_PERSONAL_ID option in .env-file!",
        not api_id: "There is no API_ID option in .env-file!",
        not api_hash: "There is no API_HASH option in .env-file!",
        not who_send: "There is no WHO_SEND option in .env-file or option is empty!"
    }
    error_message: str | None = mistakes.get(True)
    if error_message:
        raise ErrorIdHashChats(message=error_message)
    return telegram_bot_token, personal_id_chat, api_id, api_hash, who_send, time_to_wait, time_to_wait_between_send