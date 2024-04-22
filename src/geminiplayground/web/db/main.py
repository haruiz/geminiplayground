import sqlalchemy

from geminiplayground import GeminiClient
from geminiplayground.web.db.models import *
from sqlalchemy import select, insert
from geminiplayground.web.db.session_manager import sessionmanager, get_db_session
import asyncio
from dotenv import load_dotenv, find_dotenv
from .registry import mapper_registry as reg

load_dotenv(find_dotenv())


@reg.mapped_as_dataclass
class User:
    """
    User model.
    """

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.id}, {self.name})>"


async def run():
    await sessionmanager.init()
    async for session in get_db_session():
        results = await session.execute(sqlalchemy.text("SELECT name FROM sqlite_master WHERE type='table';"))
        print("Tables in the database:", results.rowcount)
        for row in results:
            print(row)


async def create_fake_users():
    users = []
    await sessionmanager.init()
    for i in range(10):
        user = {"name": f"User {i}", "email": f"user{i}@gmail.com"}
        users.append(user)
    async for session in get_db_session():
        await session.execute(insert(User), users)
        await session.commit()


async def multi_inference():
    gemini_client = GeminiClient()
    loop = asyncio.get_running_loop()

    def query_gemini():
        return gemini_client.generate_response(
            "models/gemini-1.0-pro-latest",
            "Hi!, how are you doing?, can you write a poem for me?",
        )

    # response = await loop.run_in_executor(None, query_gemini)
    # response2 = await loop.run_in_executor(None, query_gemini)
    # print(response, response2)
    results = await asyncio.gather(*[
        loop.run_in_executor(None, query_gemini) for _ in range(10)
    ])
    for task in asyncio.all_tasks():
        print(task)

    for i, result in enumerate(results):
        print("Inference", i, result)


if __name__ == '__main__':
    asyncio.run(multi_inference())
