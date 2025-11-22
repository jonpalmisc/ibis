import re
from dataclasses import dataclass
from enum import Enum


class UnsupportedAppError(Exception):
    pass


class App(Enum):
    """iBoot family application type, e.g. ROM or iBoot."""

    ROM = "SecureROM"
    IBOOT = "iBoot"

    @classmethod
    def from_banner(cls, banner: str) -> "App":
        name = re.findall(r"(\w+) for \w+,.*", banner)[0]

        match name:
            case "SecureROM":
                return cls.ROM
            case "iBoot" | "iBootStage2" | "iBSS" | "iBEC" | "AVPBooter":
                return cls.IBOOT
            case _:
                raise UnsupportedAppError(name)

    def __str__(self) -> str:
        return self.value


class TagParseError(Exception):
    pass


def version_from_tag(tag: str) -> int:
    try:
        return int(tag.split("-")[1].split(".")[0])
    except Exception as e:
        raise TagParseError(tag) from e


@dataclass
class Context:
    """Context to inform analysis."""

    app: App
    version: int

    def __init__(self, banner: str, tag: str) -> None:
        self.app = App.from_banner(banner)
        self.version = version_from_tag(tag)
