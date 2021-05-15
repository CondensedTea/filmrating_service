import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from filmrating.models.database import Base, User
from filmrating.session import create_session, sqlite_file
from filmrating.webapp import app
from tools.create_db import data


@pytest.fixture(name='tmp_database')
def fixture_tmp_database():
    engine = create_engine(sqlite_file)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def create_data(tmp_database):
    h1 = b'\xe40:\xb4\xd1g\x89\xd9\x04\x85G\xf7(pH:\xf0\x0f\x90\x99\xb5\xf00\xb2'
    h2 = b'qn\x03\x01\x08~\\"\x13\xf9\xe2\x81p\xc0\x01$@\xdd'
    session_factory = sessionmaker(tmp_database)
    with create_session(session_factory) as session:
        session.bulk_save_objects(data)
        session.add(User(login='test_dummy2', password_hash=h1 + h2))


@pytest.fixture()
def client():
    c = TestClient(app)
    return c
