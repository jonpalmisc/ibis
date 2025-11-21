import logging
import struct

from ibis.context import App, Context
from ibis.driver import Driver
from ibis.layout import Layout, Region

BANNER_OFFSET = 0x200
BUILD_TAG_OFFSET = 0x280
LAYOUT_TABLE_OFFSET = 0x300


class UnsupportedVersionError(Exception):
    pass


def _align_down(v: int, size: int) -> int:
    return v & ~(size - 1)


def _align_up(v: int, size: int) -> int:
    return _align_down(v + size - 1, size)


def _read_table(driver: Driver, count: int) -> list[int]:
    table = [
        struct.unpack("q", driver.read(LAYOUT_TABLE_OFFSET + (i * 8), 8))[0]
        for i in range(count)
    ]

    if table[0] & 0xFFF != 0:
        logging.debug("Ignoring first 3 elements of layout table... (old format)")
        table = table[3:]

    return table


def _detect_layout_v1585(context: Context, driver: Driver) -> Layout:
    table = _read_table(driver, 12)

    const_end_offset = table[2]

    cur = const_end_offset
    chunk_size = 0x800
    const_start_offset = None

    logging.debug(f"Searching backwards for CONST marker from {cur:#x}...")
    while cur > 0:
        chunk = driver.read(cur, chunk_size)

        chunk_idx = chunk.find(b"nor0\x00")
        if chunk_idx > 0:
            const_start_offset = _align_down(cur + chunk_idx, 0x10)
            break

        cur -= chunk_size

    if not const_start_offset:
        raise ValueError("oops")

    logging.debug(f"Found CONST start offset: {const_start_offset:#x}")

    text = Region(table[0], table[0] + const_start_offset, 0)
    const = Region(
        table[0] + const_start_offset, table[0] + const_end_offset, const_start_offset
    )
    data = Region(table[4], table[5], const_end_offset)
    bss = Region(table[6], table[7])

    return Layout(text, const, data, bss)


def _find_first(data: bytes, needles: list[bytes]) -> int | None:
    indices = [data.find(n) for n in needles]
    indices = [i for i in indices if i >= 0]

    return min(indices) if indices else None


def _detect_layout_v7195(context: Context, driver: Driver) -> Layout:
    table = _read_table(driver, 12)

    const_end_offset = _align_down(table[2], 0x4000) - table[0]

    cur = const_end_offset
    chunk_size = 0x4000
    const_start_offset = None

    logging.debug(f"Searching backwards for CONST marker from {cur:#x}...")
    while cur > 0:
        chunk = driver.read(cur, chunk_size)

        chunk_idx = _find_first(
            chunk, [b"nor0\x00", b"spi_nand0\x00", b"darwinos-ramdisk\x00"]
        )
        if chunk_idx:
            const_start_offset = _align_up(cur + chunk_idx, 0x10)
            break

        cur -= chunk_size

    if not const_start_offset:
        raise ValueError("oops")

    logging.debug(f"Found CONST start offset: {const_start_offset:#x}")

    const_end = _align_up(table[2], 0x4000)

    text = Region(table[0], table[0] + const_start_offset, 0)
    const = Region(table[0] + const_start_offset, const_end, const_start_offset)

    if context.app == App.ROM:
        data = Region(table[6], table[7], const_end - table[0])
    else:
        data = Region(const_end, table[7], const_end - table[0])

    bss = Region(table[7], table[8])

    return Layout(text, const, data, bss)


VERSION_MIN = 1873
VERSION_MAX = 12000


def analyze(driver: Driver) -> Layout:
    banner = driver.read_str(BANNER_OFFSET, 0x40)
    tag = driver.read_str(BUILD_TAG_OFFSET, 0x40)

    logging.debug(f"Found banner: {banner}")
    logging.debug(f"Found build tag: {tag}")

    ctx = Context(banner, tag)
    logging.info(f"Detected {ctx.app} version {ctx.version}.")

    if not (VERSION_MIN <= ctx.version < VERSION_MAX):
        raise UnsupportedVersionError(ctx.version)

    if ctx.version > 6338:
        layout = _detect_layout_v7195(ctx, driver)
    else:
        layout = _detect_layout_v1585(ctx, driver)

    for name, region in layout.regions():
        logging.debug(f"Resolved region {name}: {region}")

    logging.info("Validating layout...")
    layout.validate()

    return layout
