from abc import ABC, abstractmethod
from typing import BinaryIO, override


class Driver(ABC):
    @abstractmethod
    def read(self, offset: int, size: int) -> bytes: ...

    def read_str(self, offset: int, size: int) -> str:
        return self.read(offset, size).split(b"\x00")[0].decode().rstrip("\x00")


class BinaryIODriver(Driver):
    bio: BinaryIO

    def __init__(self, bio: BinaryIO) -> None:
        super().__init__()

        self.bio = bio

    @override
    def read(self, offset: int, size: int) -> bytes:
        self.bio.seek(offset)
        return self.bio.read(size)
