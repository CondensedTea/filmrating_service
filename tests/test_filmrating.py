from fastapi import status
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import sessionmaker

from filmrating.models.pydantic import FilmSearchValidator
from filmrating.webapp import create_session, cred_check, get_film_list

h = {'accept': 'application/json', 'Content-Type': 'application/json'}


auth_creds = ('test_dummy2', 'correcthorsebatterystaple')


def test_cred_check(tmp_database):
    auth = HTTPBasicCredentials(
        username='test_dummy2', password='correcthorsebatterystaple'
    )
    assert cred_check(auth) == auth


def test_filter_film_list(tmp_database):
    S = sessionmaker(tmp_database)
    toy = FilmSearchValidator(
        name_contains='Toy', year=None, pos_range=None, start=0, stop=9
    )
    with create_session(S) as session:
        assert get_film_list(session, toy) == [
            {'average_rating': None, 'id': 5, 'name': 'Toy Story'}
        ]


def test_register(client):
    creds = {'login': 'test_user', 'password': 's3cre7'}
    response = client.post('/register', headers=h, json=creds)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {'login': 'test_user'}


def test_get_film_list_by_name(client):
    response = client.get('/film_search?name_contains=toy', auth=auth_creds)
    assert response.status_code == 200
    assert response.json() == [{'average_rating': None, 'id': 5, 'name': 'Toy Story'}]


def test_get_film_list_by_year(client):
    response = client.get('/film_search?year=1995', auth=auth_creds)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {'average_rating': 9.0, 'id': 4, 'name': 'Seven'},
        {'average_rating': None, 'id': 5, 'name': 'Toy Story'},
    ]


def test_get_film_list_by_pos_in_top(client):
    response = client.get('/top?min_rating=8&max_rating=9', auth=auth_creds)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {'name': 'Seven', 'average_rating': 9, 'id': 4},
        {'name': 'Wing or Thigh', 'average_rating': 8, 'id': 1},
    ]


def test_get_film_list_by_range(client):
    response = client.get('/film_search?min_id=2&max_id=3', auth=auth_creds)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {'average_rating': 2.0, 'id': 2, 'name': 'La Grande Vadrouille'},
        {'average_rating': 5, 'id': 3, 'name': 'Departures'},
    ]


def test_get_film_stats_by_id(client):
    response = client.get('/film/1', auth=auth_creds)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'name': 'Wing or Thigh',
        'average_rating': 8.0,
        'ratings_count': 1,
        'reviews_count': 1,
    }


def test_rate_film(client):
    response = client.post(
        '/rate?film_id=1', auth=auth_creds, json={'rating': 10, 'text': 'very good'}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {'rating': 10, 'text': 'very good'}


def test_register_with_taken_login(client):
    creds = {'login': 'review_dummy', 'password': 'password'}
    response = client.post('/register', headers=h, json=creds)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Login is already taken'}


def test_auth_bad_login(client):
    creds = ('mike', 'password')
    response = client.get('/film/1', headers=h, auth=creds)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect login or password'}


def test_auth_bad_password(client):
    creds = ('review_dummy', 'bad_password')
    response = client.get('/film/1', headers=h, auth=creds)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect login or password'}


def test_film_stats_no_reviews(client):
    response = client.get('/film/5', auth=auth_creds)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Reviews for the film with id 5 was not found'}


def test_film_stats_bad_id(client):
    response = client.get('/film/100', auth=auth_creds)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Film with id 100 was not found'}
