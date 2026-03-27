from dataclasses import dataclass
from flask_login import UserMixin

@dataclass
class User(UserMixin):
    id: int
    username: str
    password: bytes

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

    @property
    def category(self, category: str):
        match category:
            case "Lasten peli":
                self.category_id = 1
            case "Korttipeli":
                self.category_id = 2
            case "Pakohuonepeli":
                self.category_id = 3
            case "Yhteistyöpeli":
                self.category_id = 4
            case "Sotapeli":
                self.category_id = 5
            case "Partypeli":
                self.category_id = 6
            case "Tietopeli":
                self.category_id = 7
            case "Perhepeli":
                self.category_id = 8
            case _:
                self.category_id = 0
    
    @category.getter
    def category(self) -> str:
        match self.category_id:
            case 1:
                return "Lasten peli"
            case 2:
                return "Korttipeli"
            case 3:
                return "Pakohuonepeli"
            case 4:
                return "Yhteistyöpeli"
            case 5:
                return "Sotapeli"
            case 6:
                return "Partypeli"
            case 7:
                return "Tietopeli"
            case 8:
                return "Perhepeli"
            case _:
                return "Muu"

    def from_form(form) -> 'Boardgame':
        return Boardgame(
            form["name"],
            form["number_of_players"],
            form["duration"],
            description=form["description"],
            category_id=form["category_id"],
            free_games=form["free_games"],
        )