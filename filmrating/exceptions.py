class NoFilmFound(Exception):
    def __init__(self, film_id: int) -> None:
        super().__init__()
        self.film_id = film_id


class NoReviewsFound(Exception):
    def __init__(self, film_id: int) -> None:
        super().__init__()

        self.film_id = film_id


class WrongPassword(Exception):
    def __init__(self) -> None:
        super().__init__()
