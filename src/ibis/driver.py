import logging
from abc import ABC, abstractmethod
from os import SEEK_END
from typing import BinaryIO

from ibis.context import Context


class Driver(ABC):
    # XXX: Do not use these directly, use the property functions instead; a
    # global shift need to be applied.
    _BANNER_OFFSET_RAW = 0x200
    _BUILD_TAG_OFFSET_RAW = 0x280
    _LAYOUT_TABLE_OFFSET_RAW = 0x300

    _global_shift: int = 0

    @property
    def build_tag_offset(self) -> int:
        return self._BUILD_TAG_OFFSET_RAW + self._global_shift

    @property
    def banner_offset(self) -> int:
        return self._BANNER_OFFSET_RAW + self._global_shift

    @property
    def layout_table_offset(self) -> int:
        return self._LAYOUT_TABLE_OFFSET_RAW + self._global_shift

    @abstractmethod
    def read(self, offset: int, size: int) -> bytes: ...

    @abstractmethod
    def size(self) -> int: ...

    def read_str(self, offset: int, size: int) -> str:
        return self.read(offset, size).split(b"\x00")[0].decode().rstrip("\x00")

    def detect_context(self) -> Context:
        # Traditionally the copyright banner has always been at 0x200. Starting
        # with iOS 27, it is pushed back by 0x80. Probing 0x200 for a string
        # containing "Apple" should tell us which format we have.
        if "Apple" not in self.read_str(self._BANNER_OFFSET_RAW, 0x40):
            self._global_shift = 0x80
            logging.debug("Detected iOS 27+ metadata layout.")

        banner = self.read_str(self.banner_offset, 0x40)
        tag = self.read_str(self.build_tag_offset, 0x40)

        logging.debug(f"Found banner: {banner}")
        logging.debug(f"Found build tag: {tag}")

        return Context(banner, tag)

    @staticmethod
    def _find_first(data: bytes, needles: list[bytes]) -> int | None:
        indices = [data.find(n) for n in needles]
        indices = [i for i in indices if i >= 0]

        return min(indices) if indices else None

    def find_any(
        self,
        patterns: list[bytes],
        start: int,
        end: int,
        chunk_size: int,
        backwards: bool = False,
    ) -> int | None:
        if start < 0:
            raise ValueError(f"invalid search start: {start}")

        end = min(end, self.size())
        cursor = end if backwards else start

        while True:
            chunk = self.read(cursor, chunk_size)

            if (chunk_offset := self._find_first(chunk, patterns)) is not None:
                return cursor + chunk_offset

            cursor += -chunk_size if backwards else chunk_size

            if (backwards and cursor < start) or cursor >= end:
                break

        return None


class BinaryIODriver(Driver):
    bio: BinaryIO

    def __init__(self, bio: BinaryIO) -> None:
        super().__init__()

        self.bio = bio

    # @override
    def read(self, offset: int, size: int) -> bytes:
        self.bio.seek(offset)
        return self.bio.read(size)

    # @override
    def size(self) -> int:
        self.bio.seek(0, SEEK_END)
        return self.bio.tell()
