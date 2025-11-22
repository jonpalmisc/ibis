import logging
from abc import ABC, abstractmethod
from typing import BinaryIO, override

from ibis.context import Context


class Driver(ABC):
    _BANNER_OFFSET = 0x200
    _BUILD_TAG_OFFSET = 0x280

    @abstractmethod
    def read(self, offset: int, size: int) -> bytes: ...

    def read_str(self, offset: int, size: int) -> str:
        return self.read(offset, size).split(b"\x00")[0].decode().rstrip("\x00")

    def detect_context(self) -> Context:
        banner = self.read_str(self._BANNER_OFFSET, 0x40)
        tag = self.read_str(self._BUILD_TAG_OFFSET, 0x40)

        logging.debug(f"Found banner: {banner}")
        logging.debug(f"Found build tag: {tag}")

        return Context(banner, tag)


class BinaryIODriver(Driver):
    bio: BinaryIO

    def __init__(self, bio: BinaryIO) -> None:
        super().__init__()

        self.bio = bio

    @override
    def read(self, offset: int, size: int) -> bytes:
        self.bio.seek(offset)
        return self.bio.read(size)
