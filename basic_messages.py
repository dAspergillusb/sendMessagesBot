from telebot.types import Message
from main import bot

@bot.message_handler(commands=["/start"])
async def send_welcome(message: Message) -> None:
    await bot.send_message(chat_id=message.chat.id, text="Hi, now i can send messages to you!")
    await bot.reply_to(message, "welcome message")

@bot.message_handler(commands=["/help"])
async def send_help(message: Message) -> None:
    await bot.reply_to(message, "Help Message")