from asyncio import (
    sleep,
    get_event_loop,
    set_event_loop,
    new_event_loop,
    gather, CancelledError
)
from modules import Logger

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
from itertools import count


MAXIMUM_LENGTH: int = 4096 # Maximum message length fo telegram


async def run_user_bot() -> None:
    print("Running user bot...")
    counter: count[int] = count(start=1)
    try:
        while True:
            await user_bot.main_sending(
                message=f"The messages group {next(counter)} was sent.",
                chats=env_settings.WHO_SEND
            )
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
    try:
        await gather(
            run_user_bot(),
            start_async_bot()
        )
    except KeyboardInterrupt as e:
        print(e)


if __name__ == '__main__':
    current_loop = get_event_loop()
    current_loop.run_until_complete(main())
