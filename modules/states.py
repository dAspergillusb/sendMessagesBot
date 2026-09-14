from telebot.asyncio_handler_backends import State, StatesGroup


class RegisterNewMessage(StatesGroup):
    message: State = State()
    chats: State = State()
    chat_choosing: State = State()
    chat_waiting_topic_id: State = State()
    chat_confirming: State = State()
    time_pause: State = State()

class DeleteExistingMessage(StatesGroup):
    message_id: State = State()