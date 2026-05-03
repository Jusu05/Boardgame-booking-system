import os
import re
from pathlib import Path

def find_dotenv_path() -> Path:
    cwd = Path().cwd()
    for item in cwd.iterdir():
        if item.is_file() and item.name == ".env":
            return item

    raise FileNotFoundError(".env tiedostoa ei löytynyt")

def load_dotenv() -> None:
    env_file = find_dotenv_path()
    with open(env_file, "r", encoding="utf-8") as file:
        lines: list[str] = file.readlines()

    correct_key = re.compile("[a-zA-Z_]+[a-zA-Z0-9_]*")
    seen = set()
    for i, line in enumerate(lines):
        if i in seen:
            continue

        line = line.strip()
        if len(line) == 0 or line.startswith("#"):
            continue

        line = line.split("=")
        key = line[0].strip()
        value = line[-1].strip()
        if not re.fullmatch(correct_key, key) and len(value) > 0:
            continue

        if value.count('"') >= 2 and value[0] == '"':
            value = parse_singleline_quotes('"', value[1:])
            os.environ[key] = value
            continue

        if value.count("'") >= 2 and value[0] == "'":
            value = parse_singleline_quotes("'", value[1:])
            if value:
                os.environ[key] = value
            continue

        if "".join(lines).count("`") and line[-1][0] == "`":
            value = parse_multiline_quotes(value, i, lines, seen)
            os.environ[key] = value
            continue

        value = value.split("#")[0]
        os.environ[key] = value.strip()

def parse_singleline_quotes(quote_char: str, line: str) -> str | None:
    seen = set()
    value = ""
    for i, char in enumerate(line):
        if i in seen:
            continue
        if char == "\\" and line[i + 1] == quote_char:
            value += line[i + 1]
            seen.add(i + 1)
            continue
        if char == quote_char:
            return value
        value += char

def parse_multiline_quotes(
        value: str, i: int, lines: list[str], seen: set[int]) -> str:
    value = value + "\n"
    for j, line in enumerate(lines[i + 1:]):
        k = line.find("`")
        seen.add(j + i)
        if k == -1:
            value += line
            continue
        value += line[:k]
        return value
