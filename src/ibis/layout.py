import logging
from collections.abc import Generator
from dataclasses import dataclass, fields


class MalformedRegionError(Exception):
    pass


class MalformedLayoutError(Exception):
    pass


@dataclass
class Region:
    """Bounded memory region."""

    start: int
    end: int

    file_offset: int | None = None

    @property
    def size(self) -> int:
        """Region size/length."""
        return self.end - self.start

    def is_valid(self) -> int:
        """Tells if this region is well-formed."""
        return self.end > self.start and self.size > 0

    def __gt__(self, rhs: "Region") -> bool:
        return self.start > rhs.end

    def __lt__(self, rhs: "Region") -> bool:
        return self.end < rhs.start

    def __repr__(self) -> str:
        prefix = (
            f"({self.file_offset:#x}, {self.file_offset + self.size:#x}) -> "
            if self.file_offset is not None
            else ""
        )
        return f"{prefix}({self.start:#x}, {self.end:#x})"


@dataclass
class Layout:
    """
    iBoot/SecureROM memory regions.

    Only includes memory regions that are relevant/helpful for analysis in a
    disassembler. Other regions, e.g. page tables or heap are not included.
    """

    text: Region
    const: Region
    data: Region
    bss: Region | None

    def regions(self) -> Generator[tuple[str, Region]]:
        for f in fields(self):
            if region := getattr(self, f.name):
                yield (f.name.upper(), region)

    def validate(self):
        logging.debug("Checking region order and bounds...")

        prev_name, prev_region = (None, None)
        for name, region in self.regions():
            if not region.is_valid():
                raise MalformedRegionError(f"{name}{region}")

            if prev_region and region.start < prev_region.end:
                raise MalformedLayoutError(
                    f"{name} starts below {prev_name} ({region.start:#x} < {prev_region.end:#x})"
                )

            prev_name, prev_region = name, region

        logging.debug("Layout is valid!")


FALLBACK_BSS_SIZE = 0x090000  # Largest seen in the wild is 0x07f9d0.
