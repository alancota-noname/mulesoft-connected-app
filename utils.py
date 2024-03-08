import json
import os

from pyfiglet import Figlet

figlet = Figlet(font="smslant")


# A few handy JSON types
JSON = int | str | float | bool | None | dict[str, "JSON"] | list["JSON"]
JSONObject = dict[str, JSON]
JSONList = list[JSON]


def create_banner(text: str):
    return figlet.renderText(text)


def print_json(data: dict, indent: int = 4):
    return json.dumps(
        data,
        indent=indent,
    )
