from os import makedirs
from asyncio import CancelledError, run
from sqlalchemy import (
    select,
    Result,
    Integer,
    String,
    Select,
    Sequence,
)
from sqlalchemy.exc import OperationalError, DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pathlib import Path


class Base(DeclarativeBase):
    pass


class Messages(Base):
    __tablename__ = "messages"
    message_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    chats: Mapped[str] = mapped_column(String, nullable=False)
    time_pause: Mapped[int] = mapped_column(Integer, nullable=False)

    def __str__(self) -> str:
        return (
            "Messages(\n"
            f"message_id: {self.message_id},\n"
            f"tg_id: {self.tg_id},\n"
            f"message: {self.message},\n"
            f"chats: {self.chats},\n"
            f"time_pause: {self.time_pause},\n"
            ")"
        )

    def __repr__(self) -> str:
        return (
            "Messages(\n"
            f"message_id: {self.message_id},\n"
            f"tg_id: {self.tg_id},\n"
            f"message: {self.message},\n"
            f"chats: {self.chats},\n"
            f"time_pause: {self.time_pause},\n"
            ")"
        )

    def get_chats_list(self) -> list[str | int | list[str | int]]:
        return [
            int(item) if item[1:].isnumeric()
            else item.split("/") if "@" in item and "/" in item
            else list(map(int, item.split("/"))) if "/" in item
            else item
            for item in self.chats.split(",")
        ]


class MessagesDB:

    def __init__(self, db_name: str = "messages_db", path: Path = Path("./database")):
        makedirs(str(path), exist_ok=True)
        self.db_name = db_name
        self.db_name = db_name
        self.path = path
        self.engine = self._create_engine()
        self.session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    def _create_engine(self) -> AsyncEngine:
        db: AsyncEngine = create_async_engine(f"sqlite+aiosqlite:///{self.path}/{self.db_name}.db")
        return db

    async def init_db(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
            print(f"Database initialized: {Messages.__tablename__}")

    async def get_messages(self, tg_id: int) -> list[Messages]:
        async with self.session() as session:
            query: Select[tuple[Messages]] = select(Messages).where(Messages.tg_id == tg_id)
            result: Result[tuple[Messages]] = await session.execute(query)
            return list(result.scalars().all())

    async def choose_message(self, message_id: int) -> type[Messages] | None:
        async with self.session() as session:
            if message_id:
                return await session.get(Messages, message_id)
            return None

    async def add_message(self, message_data: dict[str, str| int]) -> bool | int:
        async with self.session() as session:
            new_message: Messages = Messages(**message_data)
            session.add(new_message)
            try:
                await session.commit()
            except IntegrityError as error:
                await session.rollback()
                print(f"While executing there is an error: {error}")
                return False
            except OperationalError as error:
                await session.rollback()
                print(f"While executing there is an error: {error}")
                return False
            except DBAPIError as error:
                await session.rollback()
                print(f"While executing there is an error: {error}")
                return False
            except CancelledError as error:
                await session.rollback()
                print(f"While executing there is an error: {error}")
                return False
            return new_message.message_id

    async def change_message(self, *, data_to_change: dict[str, str | int], message_id: int) -> bool:
        if not message_id:
            return False

        message = await self.choose_message(message_id=message_id)

        async with self.session() as session:
            if message:
                for data, value in data_to_change.items():
                    if any((
                        value,
                        isinstance(value, bool),
                    )):
                        message.__setattr__(data, value)
                session.add(message)
                await session.commit()
                return True
        return False

    async def delete_message(self, message_id: int) -> bool:
        message: type[Messages] | None = await self.choose_message(message_id=message_id)
        if message:
            async with self.session() as session:
                await session.delete(message)
                try:
                    await session.commit()
                except IntegrityError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error}")
                    return False
                except OperationalError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error}")
                    return False
                except DBAPIError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error}")
                    return False
                except CancelledError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error}")
                    return False
                return True
        return False

    async def close_engine(self, db_name: str) -> None:
        await self.engine.dispose()
        del self.engine
        print(f"Pull of engine connection with {db_name} closed.")


async def main():
    database = MessagesDB()
    await database.init_db()
    await database.add_message(
        message_data={
            "tg_id": 439760043,
            "message": "Wow, t=you worked!",
            "chats": "-1003040400514/1362,-1003040400514",
            "time_pause": 3600
        }
    )
    print(*await database.get_messages(tg_id=439760043))

if __name__ == '__main__':
    run(main())
