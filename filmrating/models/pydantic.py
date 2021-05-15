from typing import Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    login: str
    password: str


class RegisterResponse(BaseModel):
    login: str


class FilmSearchValidator(BaseModel):
    name_contains: Optional[str]
    year: Optional[int]
    min_id: int = 0
    max_id: int = 5


class UserRate(BaseModel):
    rating: int = Field(ge=0, le=10)
    text: Optional[str]


class FilmStatsModel(BaseModel):
    name: str
    average_rating: float
    ratings_count: int
    reviews_count: int


class FilmModel(BaseModel):
    name: str
    average_rating: Optional[float]
    id: int
