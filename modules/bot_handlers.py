from asyncio import sleep
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_filters import StateFilter

from . import text_format as frmt
from .database import Messages, MessagesDB
from .config import env_settings
from .client import user_bot
from .states import RegisterNewMessage, DeleteExistingMessage
from pprint import pprint


async_bot: AsyncTeleBot = AsyncTeleBot(
    token=env_settings.TELEGRAM_BOT_TOKEN,
    state_storage=StateMemoryStorage(),
    colorful_logs=True
)
async_bot.add_custom_filter(custom_filter=StateFilter(async_bot))


@async_bot.message_handler(commands=["start_work"])
async def start_bot(message: types.Message) -> None:
    chat_id: int = message.chat.id
    answer_message: str = (
        f"Hi! I am a {frmt.bold('tgbot')} and I'll help you with sending messages!\n"
        "I can create new messages with list of chats, delete wrong messages and other operations.\n"
        f"Type /help' and I'll tell you what commands in my list."
    )
    await async_bot.send_message(
        chat_id=chat_id,
        text=answer_message,
        parse_mode="HTML"
    )


@async_bot.message_handler(commands=["help"])
async def help_bot(message: types.Message) -> None:
    chat_id: int = message.chat.id
    answer_message: str = (
        f"{frmt.underline('Let\'s start!')}\n\n"
        f"Type {frmt.bold('/start_work')} to start communication with me.\n"
        f"Type {frmt.bold('/help')} to see this help message.\n"
        f"Type {frmt.bold('/fast_check')} to fast test your UserBot is alive.\n"
        f"Type {frmt.bold('/deep_check')} to deep test your UserBot if fast check returned fail.\n"
        f"Type {frmt.bold('/add_new_message')} to add new messages to order of global sending.\n"
        f"Type {frmt.bold('/get_my_messages')} to get all messages that in sending list.\n"
        f"Type {frmt.bold('/delete_message')} to delete unuseful message from sending list."
    )
    await async_bot.send_message(
        chat_id=chat_id,
        text=answer_message,
        parse_mode="HTML"
    )


@async_bot.message_handler(commands=["get_my_messages"])
async def get_my_messages(message: types.Message) -> None:
    chat_id: int = message.chat.id
    messages: list[Messages] = await MessagesDB().get_messages(tg_id=env_settings.MY_PERSONAL_ID)
    if messages:
        for message in messages:
            await async_bot.send_message(
                chat_id=chat_id,
                text=str(message)
            )
            await sleep(2)
        return
    await async_bot.send_message(
        chat_id=chat_id,
        text="No messages found."
    )


@async_bot.message_handler(commands=["delete_message"])
async def delete_message(message: types.Message) -> None:
    chat_id: int = message.chat.id
    await async_bot.send_message(
        chat_id=chat_id,
        text="Input the message_id to delete it. You can check message_id with /get_my_messages command.\n"
    )
    await async_bot.set_state(
        user_id=message.from_user.id,
        state=DeleteExistingMessage.message_id,
        chat_id=chat_id
    )


@async_bot.message_handler(state=DeleteExistingMessage.message_id)
async def delete_message_from_id(message: types.Message) -> None:
    chat_id: int = message.chat.id
    if message.text and message.text.isdigit():
        message_id: int = int(message.text)
        await async_bot.send_message(
            chat_id=chat_id,
            text="Deleting..."
        )
        await MessagesDB().delete_message(message_id=message_id)
        await sleep(5)
        await async_bot.send_message(
            chat_id=chat_id,
            text="Message deleted."
        )
        await async_bot.delete_state(
            user_id=message.from_user.id,
            chat_id=chat_id
        )
    else:
        await async_bot.send_message(
            chat_id=chat_id,
            text="Please input message id (it is the number like 3)."
        )


@async_bot.message_handler(commands=["fast_check", "deep_check"])
async def check_my_user_bot(message: types.Message) -> None:
    chat_id: int = message.chat.id
    checks = {
        "/fast_check": fast_check,
        "/deep_check": deep_check
    }
    if message.text:
        result: bool = False
        try:
            result = await checks[message.text](chat_id=chat_id)
        except Exception as e:
            print(e)
            await async_bot.send_message(
                chat_id=chat_id,
                text="There is some problem with check.\n"
                "I think that your UserBot isn't start."
            )
        answers: dict[bool, str] = {
            True: "UserBot is alive! There is no problems.",
            False: "UserBot is dead. You need to check the errors in errors_log"
        }
        await sleep(2)
        await async_bot.send_message(
            chat_id=chat_id,
            text=answers[result]
        )


@async_bot.message_handler(commands=["add_new_message"])
async def add_new_message(message: types.Message) -> None:
    await async_bot.reply_to(
        message=message,
        text="Input the message you want to send."
    )
    await async_bot.set_state(
        user_id=message.from_user.id,
        state=RegisterNewMessage.message,
        chat_id=message.chat.id,
    )


@async_bot.message_handler(state=RegisterNewMessage.message)
async def register_new_message(message: types.Message) -> None:
    async with async_bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data: # type: ignore
        data["message"] = message.text

    await async_bot.set_state(
        user_id=message.from_user.id,
        state=RegisterNewMessage.chat_choosing,
        chat_id=message.chat.id,
    )
    async with async_bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data: # type: ignore
        data["chats"] = []

    await async_bot.send_message(
        chat_id=message.chat.id,
        text=(
            "Let's collect chats/groups to send message typed before.\n"
            "To do this, click the 'choose' button."
        ),
        reply_markup=get_chat_request_keyboard()
    )


@async_bot.message_handler(state=RegisterNewMessage.chat_choosing, content_types=["chat_shared", "text"])
async def handle_chat_shared(message: types.Message) -> None:
    if message.text == "Cancel":
        await async_bot.send_message(
            chat_id=message.chat.id,
            text="Ok! If you want to create new message, just input /add_new_message command."
        )
        await async_bot.delete_state(
            user_id=message.from_user.id,
            chat_id=message.chat.id
        )
        return

    chat_id: int = message.chat_shared.chat_id

    async with async_bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data: # type: ignore
        data["chat_id"] = chat_id

    await async_bot.set_state(
        user_id=message.from_user.id,
        state=RegisterNewMessage.chat_waiting_topic_id,
        chat_id=message.chat.id
    )
    await async_bot.send_message(
        chat_id=message.chat.id,
        text=f"The group '{chat_id}' is chosen.\n\n"
        "**And now is very important thing!**\n"
        "You need to go to group and look at the topic ID.\n"
        "It's look like number after '/' sign: '.../1234'.\n"
        "If there is no topics in group, just type '0' as answer.",
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()
    )


@async_bot.message_handler(state=RegisterNewMessage.chat_waiting_topic_id, content_types=["text", "any"])
async def handle_chat_waiting_topic_id(message: types.Message) -> None:
    topic_id: str | int | None = None
    if message.text and message.text.isdigit():
        topic_id = int(message.text)

    if topic_id is None:
        await async_bot.send_message(
            chat_id=message.chat.id,
            text="I can not to get the topic id from your message.\n"
            "Please, try again or type '0' if group has no topics."
        )
        return

    async with async_bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data: # type: ignore
        chat_data = f"{data["chat_id"]}/{topic_id}"
        if chat_data not in data["chats"]:
            data["chats"].append(chat_data)
            chats_count = len(data["chats"])
            text = f"Chat '{chat_data}' successfully added. Total chats: {chats_count}"
        else:
            text = f"This chat already in list"

    await async_bot.set_state(
        user_id=message.from_user.id,
        state=RegisterNewMessage.chat_confirming,
        chat_id=message.chat.id
    )
    await async_bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="Markdown"
    )
    await async_bot.send_message(
        chat_id=message.chat.id,
        text="One more chat?",
        reply_markup=get_action_keyboard()
    )


@async_bot.message_handler(state=RegisterNewMessage.chat_confirming, content_types=["text"])
async def handle_chat_action(message: types.Message) -> None:
    actions = {
        "Add another chat": add_another_chat,
        "Stop and show list": stop_chat_adding,
        "Other": other_action_before_stop_adding_chats
    }
    _message = message.text if message.text else ""
    await actions.get(_message, "Other")(message)


@async_bot.message_handler(state=RegisterNewMessage.time_pause)
async def register_chats(message: types.Message) -> None:
    time_pause = message.text
    if time_pause and all((
        ":" in time_pause,
        "," in time_pause,
        time_pause.translate(str.maketrans({":": "", ",": ""})).isdigit(),
        time_pause.split(",")[0] and time_pause.split(",")[1] != "0"
    )):
        time_pause = time_pause
        async with async_bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data: # type: ignore
            new_message: dict[str, int | str] = {
                "tg_id": message.from_user.id,
                "message": data["message"],
                "chats": ",".join(data["chats"]),
                "time_pause": time_pause
            }
            await MessagesDB().add_message(new_message)
        await async_bot.delete_state(
            user_id=message.from_user.id,
            chat_id=message.chat.id
        )
        await async_bot.send_message(
            chat_id=message.chat.id,
            text="New message added successfully. This message will be sent in the next iteration."
        )
        return
    await async_bot.send_message(
        chat_id=message.chat.id,
        text=(
            "You should send the right message!\n"
            "For example '12:00,7'"
        )
    )


async def fast_check(chat_id: int) -> bool:
    await async_bot.send_message(
        chat_id=chat_id,
        text="Start fast check..."
    )
    return await user_bot.fast_check()


async def deep_check(chat_id: int) -> bool:
    await async_bot.send_message(
        chat_id=chat_id,
        text="Start deep check..."
    )
    return await user_bot.deep_check()


async def add_another_chat(message: types.Message) -> None:
    await async_bot.set_state(
        user_id=message.from_user.id,
        state=RegisterNewMessage.chat_choosing,
        chat_id=message.chat.id
    )
    await async_bot.send_message(
        chat_id=message.chat.id,
        text="Choose the next chat/group.",
        reply_markup=get_chat_request_keyboard()
    )


async def stop_chat_adding(message: types.Message) -> None:
    async with async_bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data: # type: ignore
        final_chat_list: list[int | str] = data.get("chats", [])

    if not final_chat_list:
        await async_bot.send_message(
            chat_id=message.chat.id,
            text="There is no one chat chosen. Retry your action."
        )
        await async_bot.delete_state(
            user_id=message.from_user.id,
            chat_id=message.chat.id
        )
        return

    await async_bot.set_state(
        user_id=message.from_user.id,
        state=RegisterNewMessage.time_pause,
        chat_id=message.chat.id
    )
    formatted_chats_list = "\n".join(f"• '{chat_id}'" for chat_id in final_chat_list)
    await async_bot.send_message(
        chat_id=message.chat.id,
        text=f"**There is your chosen chats**\n\n{formatted_chats_list}",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await sleep(1)
    await async_bot.send_message(
        chat_id=message.chat.id,
        text=(
            "Input the time when message should be sent and period of pause between sending.\n"
            "Type this like '12:00,7' (at 12PM over every 7 days)."
        )
    )


async def other_action_before_stop_adding_chats(message: types.Message) -> None:
    await async_bot.send_message(
        chat_id=message.chat.id,
        text="Please, use only buttons for actions!"
    )

async def send_critical_alert(alert: str) -> None:
    await async_bot.send_message(
        chat_id=env_settings.MY_PERSONAL_ID,
        text=alert
    )


def get_chat_request_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    choose = types.KeyboardButton(
        text="Choose",
        request_chat=types.KeyboardButtonRequestChat(request_id=100, chat_is_channel=False)
    )
    cancel = types.KeyboardButton(
        text="Cancel"
    )
    markup.add(choose)
    markup.add(cancel)
    return markup


def get_action_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_add = types.KeyboardButton(text="Add another chat")
    button_stop = types.KeyboardButton(text="Stop and show list")
    markup.add(button_add)
    markup.add(button_stop)
    return markup
