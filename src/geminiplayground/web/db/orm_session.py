import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from geminiplayground.utils import get_gemini_playground_cache_dir

# create the engine and enable foreign key constraint
cache_dir = get_gemini_playground_cache_dir()
database_file = os.path.join(cache_dir, "data.db")
database_uri = f"sqlite:///{database_file}"
engine = create_engine(database_uri, echo=False)


def _fk_pragma_on_connect(dbapi_con, con_record):
    print("Enabling foreign key constraint")
    dbapi_con.execute("pragma foreign_keys=ON")


event.listen(engine, "connect", _fk_pragma_on_connect)
# create the session maker
SessionMaker = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)
