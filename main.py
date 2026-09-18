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
from datetime import datetime
from time import time
from random import randint

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
SLEEP_BETWEEN: list[int] = [5, 30] # sleep between some actions
ONE_DAY_IN_SECONDS: int = 86400 # Seconds count for one day


async def run_user_bot() -> None:
    print("Running user bot...")
    try:
        while True:
            logger.create_log_info(
                msg="UserBot starting new session..."
            )
            messages: list[Messages] = await MessagesDB().get_messages(tg_id=env_settings.MY_PERSONAL_ID)
            if not messages:
                await sleep(randint(*SLEEP_BETWEEN))
            else:
                for message_data in messages:
                    _time, pause = message_data.time_pause.split(",")
                    period: int | float = ((time() - message_data.sent_time) // ONE_DAY_IN_SECONDS) if message_data.sent_time else int(pause)
                    can_be_sent: bool = _time <= datetime.now().time().strftime("%H:%M")
                    if can_be_sent and period >= int(pause):
                        logger.create_log_info(
                            msg=f"Sending message {message_data.message_id}...",
                        )
                        await user_bot.main_sending(
                            message=message_data.message,
                            chats=message_data.get_chats_list()
                        )
                        await MessagesDB().change_message(
                            data_to_change={"sent_time": int(time())},
                            message_id=message_data.message_id
                        )
                        await sleep(randint(*SLEEP_BETWEEN))
                        logger.create_log_info(
                            msg="Messages has sent successfully.",
                        )
                    else:
                        logger.create_log_info(
                            msg=f"The messages has not been sent: {period=} <= {pause=}; {can_be_sent=}"
                        )
                logger.create_log_info(
                    msg="UserBot complete session."
                )
                logger.create_log_info(
                    msg="Pause between sending..."
                )
                await sleep(randint(*SLEEP_BETWEEN))
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


