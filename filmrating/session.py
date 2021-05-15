import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

if os.environ.get('TESTING'):
    sqlite_file = 'sqlite:///filmrating/test.sqlite3'
else:
    sqlite_file = 'sqlite:///filmrating/filmrating_db.sqlite3'


engine: Engine = create_engine(sqlite_file, echo=False)
session_factory = sessionmaker(bind=engine)


@contextmanager
def create_session(sf: sessionmaker = session_factory) -> Iterator[Session]:
    new_session: Session = sf()
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()
