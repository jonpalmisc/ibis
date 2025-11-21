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
            case "iBoot" | "iBSS" | "iBEC" | "AVPBooter":
                return cls.IBOOT
            case _:
                raise UnsupportedAppError(name)

    def __str__(self) -> str:
        return self.value


@dataclass
class Context:
    """Context to inform analysis."""

    app: App
    version: int

    def __init__(self, banner: str, tag: str) -> None:
        self.app = App.from_banner(banner)
        self.version = int(tag.split("-")[1].split(".")[0])
