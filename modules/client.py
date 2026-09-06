from asyncio import sleep
from pyrogram import Client
from pyrogram.errors import (
    FloodWait,
    PeerFlood,
    PeerIdInvalid,
    ChatWriteForbidden,
    UserIsBlocked,
    MessageEmpty,
    MessageTooLong,
    AuthKeyInvalid,
    SessionExpired,
    RPCError
)
from datetime import datetime
from .errors import ErrorOccurred
from .config import env_settings


class SendMessage(Client):

    def __init__(self, name: str, api_id: int | str, api_hash: str | str):
        super().__init__(
            name=name,
            api_id=api_id,
            api_hash=api_hash
        )
        self.started_work: bool = False

    async def check_me(self):
        return self.started_work

    async def main_sending(self, message: str, chats: list[str | int | list[int]]) -> None:
        self.started_work = not self.started_work
        async with self:
            report: list[str] = ["----------\n", "UserBot:\n", "Start messaging...\n"]
            problems_count: int = 0

            for chat in chats:
                current_chat_type: dict[str, int | str | None] = {
                    "chat_id": 0,
                    "thread_id": None
                }
                if isinstance(chat, str | int):
                    current_chat_type["chat_id"] = chat
                if isinstance(chat, list):
                    current_chat_type["chat_id"] = chat[0]
                    current_chat_type["thread_id"] = chat[1]
                if not current_chat_type["chat_id"]:
                    await self.send_message(
                        chat_id="me",
                        text=f"There is something wrong with {chat}. There is no chat_type?\nSkipping it."
                    )
                    continue
                try:
                    await self.send_message(
                        chat_id=current_chat_type["chat_id"],
                        message_thread_id=int(current_chat_type["thread_id"]),
                        text=message
                    )
                    report.append(f"{datetime.now().strftime(format="%d.%m.%Y::%H.%M.%S")} – Message sent to {chat}\n")
                    await sleep(env_settings.TIME_TO_WAIT)
                except FloodWait as flood:
                    problems_count += 1
                    await sleep(flood.value)
                    await self.send_message(
                        chat_id="me",
                        text=f"UserBot: There is a problem with flood. The Telegram ask me wait for {flood.value} seconds."
                    )
                    await sleep(env_settings.TIME_TO_WAIT)
                    await self.send_message(
                        chat_id=current_chat_type["chat_id"],
                        message_thread_id=current_chat_type["thread_id"],
                        text=message
                    )
                    report.append(f"Message sent to {chat}\n")
                    await sleep(env_settings.TIME_TO_WAIT)
                except PeerFlood as peer:
                    await self.send_message(
                        chat_id="me",
                        text=f"UserBot: I think I get the ban for flood. It is very bad thing... See the errors_logs."
                    )
                    self.started_work = not self.started_work
                    raise ErrorOccurred(
                        message=f"There is very bad problem occurred while sending messages!\nError message is: {peer.MESSAGE}"
                    )
                except PeerIdInvalid as peer:
                    problems_count += 1
                    await self.send_message(
                        chat_id="me",
                        text=f"UserBot: The id or name of chat {chat} is invalid! Check your .env-file.\nError message: {peer.MESSAGE}"
                    )
                    await sleep(env_settings.TIME_TO_WAIT)
                except ChatWriteForbidden as write_forbidden:
                    problems_count += 1
                    await self.send_message(
                        chat_id="me",
                        text=f"UserBot: There is error occurred with sending the message to chat {chat}\nI think you need to check the chat permissions to you.\nError message: {write_forbidden.MESSAGE}"
                    )
                    await sleep(env_settings.TIME_TO_WAIT)
                except UserIsBlocked as blocked_user:
                    problems_count += 1
                    await self.send_message(
                        chat_id="me",
                        text=f"UserBot: I tried to write the message to {chat}, but he has blocked me (e.g. your account).\nI think i need to remove this chat from chat list.\nError message: {blocked_user.MESSAGE}"
                    )
                    chats.remove(chat)
                    await sleep(env_settings.TIME_TO_WAIT)
                except MessageEmpty as empty_message:
                    await self.send_message(
                        chat_id="me",
                        text=f"UserBot: Hey, I don't want to send empty messages.\nCheck your message-file.\nError message: {empty_message.MESSAGE}"
                    )
                    self.started_work = not self.started_work
                    raise ErrorOccurred(
                        message=empty_message.MESSAGE
                    )
                except MessageTooLong as message_too_long:
                    await self.send_message(
                        chat_id="me",
                        text=f"UserBot: The message that I've tried to send is very long. Your need to make it some shorter (delete {len(message) - 4096} chars).\nError message: {message_too_long.MESSAGE}" #TODO
                    )
                    self.started_work = not self.started_work
                    raise ErrorOccurred(
                        message=message_too_long.MESSAGE
                    )
                except AuthKeyInvalid as auth_key:
                    self.started_work = not self.started_work
                    raise ErrorOccurred(
                        message=auth_key.MESSAGE
                    )
                except SessionExpired as session_expired:
                    self.started_work = not self.started_work
                    raise ErrorOccurred(
                        message=session_expired.MESSAGE
                    )
                except RPCError as err:
                    self.started_work = not self.started_work
                    raise ErrorOccurred(
                        message=err.MESSAGE
                    )
            else:
                report.extend(
                    [
                        "All messages have been sent successfully.",
                        "----------\n"
                    ]
                )
                await self.send_message(
                    chat_id="me",
                    text="".join(report)
                )


user_bot = SendMessage(
    name="my_account",
    api_id=env_settings.API_ID,
    api_hash=env_settings.API_HASH,
)