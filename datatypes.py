from dataclasses import dataclass
from security import UserMixin

@dataclass
class User(UserMixin):
    id: int
    username: str
    password: str


class Boardgame:
    def __init__(self, name: str, number_of_players: int , duration: int, id: int | None = None, description: int | None = None, category_id: int | None = None, free_games: int | None = None, reserved_games: int | None = None):
        self.name = name
        self.description = description
        self.number_of_players = number_of_players
        self.duration = duration
        self.id = id
        self.category_id = category_id
        self.free_games = free_games
        self.reserved_games = reserved_games

    def from_form(form) -> 'Boardgame':
        return Boardgame(
            form["name"],
            form["number_of_players"],
            form["duration"],
            description=form["description"],
            category_id=form["category_id"],
            free_games=form["free_games"],
        )

class Review:
    def __init__(self, user: str, review: str | None, stars: float):
        self.user = user
        self.review = review
        self.rating = stars
        self.stars = int(stars)
        self.half = False

        frac = stars - self.stars
        if 0.25 <= frac <= 0.75:
            self.half = True
        elif frac > 0.75 and self.stars <= 5:
            self.stars += 1

    def __add__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating + other.rating
        elif isinstance(other, int):
            return self.rating + other
        elif isinstance(other, float):
            return self.rating + other
        else:
            return ValueError(f"Can't add Review and {type(other)}")

    def __sub__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating - other.rating
        elif isinstance(other, int):
            return self.rating - other
        elif isinstance(other, float):
            return self.rating - other
        else:
            return ValueError(f"Can't subtract Review and {type(other)}")

    def __mul__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating * other.rating
        elif isinstance(other, int):
            return self.rating * other
        elif isinstance(other, float):
            return self.rating * other
        else:
            return ValueError(f"Can't multiple Review and {type(other)}")

    def __truediv__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating / other.rating
        elif isinstance(other, int):
            return self.rating / other
        elif isinstance(other, float):
            return self.rating / other
        else:
            return ValueError(f"Can't divide Review and {type(other)}")

    def __floordiv__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating // other.rating
        elif isinstance(other, int):
            return self.rating // other
        elif isinstance(other, float):
            return self.rating // other
        else:
            return ValueError(f"Can't floor divide Review and {type(other)}")

    def __pow__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating ** other.rating
        elif isinstance(other, int):
            return self.rating ** other
        elif isinstance(other, float):
            return self.rating ** other
        else:
            return ValueError(f"Can't get power Review and {type(other)}")
