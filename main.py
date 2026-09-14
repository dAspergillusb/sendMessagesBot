from asyncio import (
    sleep,
    get_event_loop,
    set_event_loop,
    new_event_loop,
    gather,
    shield,
    CancelledError
)
from modules import Logger, MessagesDB, Messages

logger: Logger = Logger(
    to_file=True,
    to_stdout=True
)

try:
    get_event_loop()
except RuntimeError:
    loop = new_event_loop()
    set_event_loop(loop)

from aiofiles import open
from modules import (
    env_settings,
    async_bot,
    user_bot,
    ErrorOccurred,
)


MAXIMUM_LENGTH: int = 4096 # Maximum message length for telegram


async def run_user_bot() -> None:
    print("Running user bot...")
    try:
        while True:
            messages: list[Messages] = await MessagesDB().get_messages(tg_id=env_settings.MY_PERSONAL_ID)
            if not messages:
                await sleep(240)
            else:
                for message_data in messages:
                    await user_bot.main_sending(
                        message=message_data.message,
                        chats=message_data.get_chats_list()
                    )
                    await sleep(240) # Sleep 4 minutes between message group
                await sleep(env_settings.TIME_TO_WAIT_BETWEEN_SEND)
    except ErrorOccurred as error:
        alert: str = (
            "There is a problem with your bot!\n"
            f"The problem is: {error.MESSAGE}\n"
            "You need to fix something. Check it!"
        )
        await async_bot.send_message(
            chat_id=env_settings.MY_PERSONAL_ID,
            text=alert
        )
        to_error_log: str = "\n".join([
            "##########",
            alert,
            "##########"
        ])
        async with open("./logs/error_logs", "a") as error_log:
            await error_log.write(f"{to_error_log}\n\n")


async def start_async_bot() -> None:
    print("Starting async bot...")
    try:
        await async_bot.infinity_polling()
    except KeyboardInterrupt:
        print("Stopping AsyncTeleBot...")
    except CancelledError:
        print("Stopping AsyncTeleBot...")
    finally:
        await async_bot.close_session()
        print("AsyncTeleBot has stopped!")


async def main() -> None:
    await MessagesDB().init_db()
    await gather(
        run_user_bot(),
        start_async_bot()
    )


async def stop_all() -> None:
    if hasattr(user_bot, "is_connected") and user_bot.is_connected:
        try:
            print("Stopping UserBot...")
            await user_bot.stop(block=False)
            print("UserBot has stopped!")
        except Exception as e:
            print(e)


    print("Stopping Telegram bot...")
    try:
        await shield(async_bot.close_session())
    except Exception as e:
        print(e)
    print("Telegram bot has stopped!")

    print("Stopping Logger...")
    logger.stop()
    print("Logger has stopped!")


if __name__ == '__main__':
    current_loop = get_event_loop()
    try:
        current_loop.run_until_complete(main())
    except (KeyboardInterrupt, CancelledError):
        print("I checked cancel signal. Stopping system safety...")

        current_loop.run_until_complete(stop_all())

        # print("Stopping main_loop...")
        # current_loop.close()
        # print("main_loop has stopped!")


