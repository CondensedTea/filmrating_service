from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
    and_,
    func,
    select,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    login = Column(String, unique=True, nullable=False)
    password_hash = Column(LargeBinary, nullable=False)


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    film_id = Column(Integer, ForeignKey('films.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(
        Integer,
        CheckConstraint('rating >= 0'),
        CheckConstraint('rating <= 10'),
        nullable=False,
    )
    text = Column(String)
    timestamp = Column(DateTime)
    __table_args__ = (UniqueConstraint('film_id', 'user_id'),)


class Film(Base):
    __tablename__ = 'films'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String)
    year = Column(Integer)
    review_count = column_property(
        select([func.count(Review.id)]).where(
            and_(Review.film_id == id, Review.text.isnot(None))
        )
    )
    rating_count = column_property(
        select([func.count(Review.id)]).where(Review.film_id == id)
    )
    average_rating = column_property(
        select([func.avg(Review.rating)]).where(Review.film_id == id)
    )
