from dataclasses import dataclass
from security import UserMixin


@dataclass
class User(UserMixin):
    id: int
    username: str
    password: str


class Boardgame:
    def __init__(self, name: str, number_of_players: int, duration: int, id: int | None = None, description: int | None = None, free_games: int | None = None, reserved_games: int | None = None, category: str | None = None, category_id: int | None = None, stars: int | None = None, half_star: bool | None = None):
        self.name = name
        self.description = description
        self.number_of_players = number_of_players
        self.duration = duration
        self.id = id
        self.free_games = free_games
        self.reserved_games = reserved_games
        self.category = category
        self.category_id = category_id
        self.stars = stars
        self.half_star = half_star

    def from_form(form) -> 'Boardgame':
        return Boardgame(
            form["name"],
            form["number_of_players"],
            form["duration"],
            description=form["description"],
            free_games=form["free_games"],
            category_id=form["category_id"],
        )


class Review:
    def __init__(self, user: str, text: str | None, rating: float, stars: int | None, half_star: bool | None, user_avatar):
        self.user = user
        self.user_avatar = user_avatar
        self.text = text
        self.rating = rating
        self.stars = stars
        self.half_star = half_star

    def __add__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating + other.rating
        elif isinstance(other, int):
            return self.rating + other
        elif isinstance(other, float):
            return self.rating + other
        else:
            raise ValueError(f"Can't add Review and {type(other)}")

    def __radd__(self, other) -> float:
        if isinstance(other, Review):
            return other.rating + self.rating
        elif isinstance(other, int):
            return other + self.rating
        elif isinstance(other, float):
            return other + self.rating
        else:
            raise ValueError(f"Can't add Review and {type(other)}")

    def __sub__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating - other.rating
        elif isinstance(other, int):
            return self.rating - other
        elif isinstance(other, float):
            return self.rating - other
        else:
            raise ValueError(f"Can't subtract Review and {type(other)}")

    def __rsub__(self, other) -> float:
        if isinstance(other, Review):
            return other.rating - self.rating
        elif isinstance(other, int):
            return other - self.rating
        elif isinstance(other, float):
            return other - self.rating
        else:
            raise ValueError(f"Can't subtract Review and {type(other)}")

    def __mul__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating * other.rating
        elif isinstance(other, int):
            return self.rating * other
        elif isinstance(other, float):
            return self.rating * other
        else:
            raise ValueError(f"Can't multiple Review and {type(other)}")

    def __rmul__(self, other) -> float:
        return self.__mul__(other)

    def __truediv__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating / other.rating
        elif isinstance(other, int):
            return self.rating / other
        elif isinstance(other, float):
            return self.rating / other
        else:
            raise ValueError(f"Can't divide Review and {type(other)}")

    def __rtruediv__(self, other) -> float:
        if isinstance(other, Review):
            return other.rating / self.rating
        elif isinstance(other, int):
            return other / self.rating
        elif isinstance(other, float):
            return other / self.rating
        else:
            raise ValueError(f"Can't divide Review and {type(other)}")

    def __floordiv__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating // other.rating
        elif isinstance(other, int):
            return self.rating // other
        elif isinstance(other, float):
            return self.rating // other
        else:
            raise ValueError(f"Can't floor divide Review and {type(other)}")

    def __rfloordiv__(self, other) -> float:
        if isinstance(other, Review):
            return other.rating // self.rating
        elif isinstance(other, int):
            return other // self.rating
        elif isinstance(other, float):
            return other // self.rating
        else:
            raise ValueError(f"Can't floor divide Review and {type(other)}")

    def __pow__(self, other) -> float:
        if isinstance(other, Review):
            return self.rating ** other.rating
        elif isinstance(other, int):
            return self.rating ** other
        elif isinstance(other, float):
            return self.rating ** other
        else:
            raise ValueError(f"Can't get power Review and {type(other)}")

    def __rpow__(self, other) -> float:
        if isinstance(other, Review):
            return other.rating ** self.rating
        elif isinstance(other, int):
            return other ** self.rating
        elif isinstance(other, float):
            return other ** self.rating
        else:
            raise ValueError(f"Can't get power Review and {type(other)}")
