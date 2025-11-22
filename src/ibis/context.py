import re
from dataclasses import dataclass
from enum import Enum


class BannerParseError(Exception):
    pass


def _parse_banner(banner: str) -> tuple[str, str]:
    try:
        return re.findall(r"(\w+) for (\w+),.*", banner)[0]
    except Exception as e:
        raise BannerParseError(banner) from e


class UnsupportedAppError(Exception):
    pass


class App(Enum):
    """iBoot family application type, e.g. ROM or iBoot."""

    ROM = "SecureROM"
    IBOOT = "iBoot"
    AVPBOOTER = "AVPBooter"

    @classmethod
    def parse(cls, name: str):
        match name:
            case "SecureROM":
                return cls.ROM
            case "iBoot" | "iBootStage2" | "iBSS" | "iBEC":
                return cls.IBOOT
            case "AVPBooter":
                return cls.AVPBOOTER
            case _:
                raise UnsupportedAppError(name)

    def __str__(self) -> str:
        return self.value


class TagParseError(Exception):
    pass


class Version:
    _parts: list[int]

    def __init__(self, tag: str):
        try:
            version = tag.split("-")[1]
            self._parts = [int(p) for p in version.split(".")]
        except Exception as e:
            raise TagParseError(tag) from e

    @property
    def major(self) -> int:
        return self._parts[0]

    def __str__(self) -> str:
        return ".".join(str(p) for p in self._parts)


@dataclass
class Context:
    """Context to inform analysis."""

    app: App
    version: Version
    target: str

    def __init__(self, banner: str, tag: str) -> None:
        app, self.target = _parse_banner(banner)

        self.app = App.parse(app)
        self.version = Version(tag)
