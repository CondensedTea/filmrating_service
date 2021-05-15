import hashlib
import os
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from filmrating.exceptions import NoFilmFound, NoReviewsFound, WrongPassword
from filmrating.models.database import Film, Review, User
from filmrating.models.pydantic import (
    FilmModel,
    FilmSearchValidator,
    FilmStatsModel,
    RegisterRequest,
    RegisterResponse,
    UserRate,
)
from filmrating.session import create_session

app = FastAPI()

security = HTTPBasic()


def cred_check(
    credentials: HTTPBasicCredentials = Depends(security),
) -> HTTPBasicCredentials:
    with create_session() as session:
        try:
            user: User = (
                session.query(User).filter(User.login == credentials.username).one()
            )
        except NoResultFound as e:
            raise WrongPassword from e
        salt = user.password_hash[:10]
        correct_password_hash = user.password_hash[10:]
        possible_password_hash = hashlib.pbkdf2_hmac(
            'sha256', credentials.password.encode('utf-8'), salt, 100000
        )
        if not possible_password_hash == correct_password_hash:
            raise WrongPassword
        return credentials


def get_film_list(session: Session, params: FilmSearchValidator) -> List[FilmModel]:
    film_query = session.query(Film)
    if params.year:
        film_query = film_query.filter(Film.year == params.year)
    if params.name_contains:
        film_query = film_query.filter(
            Film.name.like('%{}%'.format(params.name_contains))
        )
    return_list = []
    film_list = film_query.filter(
        Film.id >= params.min_id, Film.id <= params.max_id
    ).all()
    for f in film_list:
        return_list.append(
            FilmModel(name=f.name, average_rating=f.average_rating, id=f.id)
        )
    return return_list


def get_film_top(session: Session, min_rating: int, max_rating: int) -> List[FilmModel]:
    film_query = (
        session.query(Film)
        .filter(Film.average_rating.isnot(None))
        .order_by(Film.average_rating.desc())
    )
    return_list = []
    top = film_query.filter(Film.average_rating.between(min_rating, max_rating)).all()
    for f in top:
        return_list.append(
            FilmModel(name=f.name, average_rating=f.average_rating, id=f.id)
        )
    return return_list


def get_film(session: Session, film_id: int) -> FilmStatsModel:
    try:
        film = session.query(Film).filter(Film.id == film_id).one()
    except NoResultFound as e:
        raise NoFilmFound(film_id=film_id) from e
    if film.average_rating is None:
        raise NoReviewsFound(film_id=film_id)
    response = FilmStatsModel(
        name=film.name,
        average_rating=film.average_rating,
        ratings_count=film.rating_count,
        reviews_count=film.review_count,
    )
    return response


@app.exception_handler(NoReviewsFound)
def no_reviews_found_handler(responce: Response, exc: NoReviewsFound) -> Response:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            'detail': 'Reviews for the film with id %s was not found' % exc.film_id
        },
    )


@app.exception_handler(NoFilmFound)
def no_film_found_handler(responce: Response, exc: NoFilmFound) -> Response:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'detail': 'Film with id %s was not found' % exc.film_id},
    )


@app.exception_handler(WrongPassword)
def wrong_password_handler(responce: Response, exc: WrongPassword) -> Response:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': 'Incorrect login or password'},
        headers={'WWW-Authenticate': 'Basic'},
    )


@app.post(
    '/register', status_code=status.HTTP_202_ACCEPTED, response_model=RegisterResponse
)
def register(user: RegisterRequest) -> RegisterResponse:
    salt: bytes = os.urandom(10)
    password_hash: bytes = salt + hashlib.pbkdf2_hmac(
        'sha256', user.password.encode('utf-8'), salt, 100000
    )
    try:
        with create_session() as session:
            session.add(User(login=user.login, password_hash=password_hash))
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Login is already taken',
        ) from e
    return RegisterResponse(login=user.login)


@app.post('/rate', status_code=status.HTTP_201_CREATED, response_model=UserRate)
def rate(
    film_id: int,
    params: UserRate,
    credentials: HTTPBasicCredentials = Depends(cred_check),
) -> UserRate:
    with create_session() as session:
        user = session.query(User).filter(User.login == credentials.username).one()
        session.add(
            Review(
                user_id=user.id,
                film_id=film_id,
                rating=params.rating,
                text=params.text,
                timestamp=datetime.now(),
            )
        )
        return UserRate(rating=params.rating, text=params.text)


@app.get(
    '/film_search',
    status_code=status.HTTP_200_OK,
    response_model=List[FilmModel],
)
def film_search(
    name_contains: Optional[str] = None,
    year: Optional[int] = None,
    min_id: int = 0,
    max_id: int = 5,
    credentials: HTTPBasicCredentials = Depends(cred_check),
) -> List[FilmModel]:
    with create_session() as session:
        query = FilmSearchValidator(
            name_contains=name_contains, year=year, min_id=min_id, max_id=max_id
        )
        return get_film_list(session, query)


@app.get(
    '/film/{film_id}', status_code=status.HTTP_200_OK, response_model=FilmStatsModel
)
def film_info(
    film_id: int, credentials: HTTPBasicCredentials = Depends(cred_check)
) -> FilmStatsModel:
    with create_session() as session:
        return get_film(session, film_id)


@app.get('/top', status_code=status.HTTP_200_OK, response_model=List[FilmModel])
def film_top(
    min_rating: int = 1,
    max_rating: int = 10,
    credentials: HTTPBasicCredentials = Depends(cred_check),
) -> List[FilmModel]:
    with create_session() as session:
        return get_film_top(session, min_rating, max_rating)
