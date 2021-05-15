# Сервис оценки фильмов
Сервис оценки фильмов, в котором, после регистрации, можно: 
1. Ставить оценки фильмам и писать отзывы
2. Искать фильмы по подстроке в названии или году выхода, выдачу можно ограничить параметрами start/stop 
3. Получить топ N фильмов по среднему рейтингу
4. Получить информацию о фильме по id: название, количество отзывов, количество оценок и среднюю оценку.

Для управления сервисом можно воспользоваться админ-панелью, в которой можно: 
1. Добавлять / удалять фильмы
2. Просматривать список пользователей
3. Просматривать отзывы каждого пользователя
4. Менять текст любого отзыва.
    
### Create venv:
    make venv

### Run tests:
    make test
    
### Run linters:
    make lint
    
### Run formatters:
    make format
    
### Initialise SQLite3 DB:
    make db

### Run service:
    make up

### Run admin panel:
    make admin