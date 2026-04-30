from dataclasses import dataclass
from security import UserMixin, current_user


@dataclass
class User(UserMixin):
    id: int
    username: str
    password: str


class Photo:
    def __init__(self, name: str | None, id: int | None, file_type: str | None, bytes: bytes | None) -> None:
        self.name = name
        self.id = id
        self.file_type = file_type
        self.bytes = bytes


class Boardgame:
    def __init__(self, name: str, number_of_players: int, duration: int, id: int | None = None, description: int | None = None, free_games: int | None = None, reserved_games: int | None = None, category: str | None = None, category_id: int | None = None, stars: int | None = None, half_star: bool | None = None, number_of_photos: bool | None = None) -> None:
        self.name = name
        self.description = description
        self.number_of_players = number_of_players
        self.duration = duration
        self.id = id
        self.free = free_games
        self.reserved = reserved_games
        self.category = category
        self.category_id = category_id
        self.stars = stars
        self.half_star = half_star
        self.number_of_photos = number_of_photos

    def update(self, form: dict) -> None:
        self.number_of_players = form["number_of_players"]
        self.duration = form["duration"]
        self.description = form["description"]
        self.category_id = int(form["category_id"])

    def from_form(form: dict) -> 'Boardgame':
        return Boardgame(
            form["name"],
            int(form["number_of_players"]),
            float(form["duration"]),
            description=form["description"],
            category_id=int(form["category_id"]),
        )


class Review:
    def __init__(self, user: User, text: str | None, rating: float, stars: int | None = None, half_star: bool | None = None):
        self.user = user
        self.text = text
        self.rating = rating
        self.stars = stars
        self.half_star = half_star

    def from_form(form) -> 'Review':
        return Review(
            current_user,
            form["text"],
            float(form["rating"])
        )

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