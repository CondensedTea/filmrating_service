from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from filmrating.models.database import Base, Film, Review, User
from filmrating.session import sqlite_file

data = [
    User(login='review_dummy', password_hash=b'blank'),
    Film(name='Wing or Thigh', year=1976),
    Film(name='La Grande Vadrouille', year=1966),
    Film(name='Departures', year=2008),
    Film(name='Seven', year=1995),
    Film(name='Toy Story', year=1995),
    Film(name='Forest Gump', year=1994),
    Review(film_id=1, user_id=1, rating=8, text='very funny'),
    Review(film_id=2, user_id=1, rating=2, text='didnt laugh'),
    Review(film_id=3, user_id=1, rating=5, text='good for one time'),
    Review(film_id=4, user_id=1, rating=9),
]


def create_db(f: str) -> Engine:
    e = create_engine(f, echo=True)
    Base.metadata.create_all(e)
    return e


def insert_data(engine: Engine) -> None:
    Session = sessionmaker(engine)
    session = Session()
    session.bulk_save_objects(data)
    session.commit()


if __name__ == '__main__':
    eng = create_db(sqlite_file)
    insert_data(eng)
