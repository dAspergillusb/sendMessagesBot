from telebot import types
from telebot.async_telebot import AsyncTeleBot
from .config import env_settings
from .client import user_bot


async_bot: AsyncTeleBot = AsyncTeleBot(
    token=env_settings.TELEGRAM_BOT_TOKEN,
    colorful_logs=True
)


@async_bot.message_handler(commands=["start_messaging"])
async def start_messaging(message: types.Message) -> None:
    chat_id: int = message.chat.id
    await async_bot.send_message(
        chat_id=chat_id,
        text="Hi, i'm here!"
    )


@async_bot.message_handler(commands=["checkMyUserBot"])
async def check_my_user_bot(message: types.Message):
    chat_id: int = message.chat.id
    await async_bot.send_message(
        chat_id=chat_id,
        text="Ok! I started checking your UserBot..."
    )
    check: bool = await user_bot.check_me()
    await async_bot.send_message(
        chat_id=chat_id,
        text="Check has finished!"
    )
    checked: dict[bool, str] = {
        check: "UserBot is alive! There is no problems.",
        not check: "UserBot is dead. You need to check the errors in errors_log"
    }
    await async_bot.send_message(
        chat_id=chat_id,
        text=checked[True]
    )


async def send_critical_alert(alert: str) -> None:
    await async_bot.send_message(
        chat_id=env_settings.MY_PERSONAL_ID,
        text=alert
    )