from aiohttp import ClientSession
from ..main import TELEGRAM_BOT_TOKEN, MY_PERSONAL_ID


class AlertCriticalError:
    """
    Class that asynchronously sent the critical error to UserBot owner via telegram bot.
    """

    def __init__(self, alert_message: str) -> None:
        self.alert_message = alert_message

    async def send_alert(self) -> None:
        alert_text = (
            f"UserBot crashed with critical error!"
            f"Error message: {self.alert_message}"
            f"You need to restart the UserBot, renew the session, or it may be some another error (if it see error_logs)"
        )
        bot_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": MY_PERSONAL_ID,
            "text": self.alert_message,
            "parse_mode": "Markdown"
        }
        async with ClientSession() as session:
            try:
                async with session.post(bot_url, json=payload, timeout=30) as response:
                    pass
            except Exception:
                pass