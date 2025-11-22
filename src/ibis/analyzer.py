import logging
import struct

from ibis.context import App, Context
from ibis.driver import Driver
from ibis.layout import Layout, Region


class UnsupportedVersionError(Exception):
    pass


class AnalysisError(Exception):
    pass


def _align_down(v: int, size: int) -> int:
    return v & ~(size - 1)


def _align_up(v: int, size: int) -> int:
    return _align_down(v + size - 1, size)


_LAYOUT_TABLE_OFFSET = 0x300


def _read_table(driver: Driver, count: int) -> list[int]:
    table = [
        struct.unpack("q", driver.read(_LAYOUT_TABLE_OFFSET + (i * 8), 8))[0]
        for i in range(count)
    ]

    if table[0] & 0xFFF != 0:
        logging.debug("Ignoring first 3 elements of layout table... (old format)")
        table = table[3:]

    return table


def _detect_layout_v1585(_: Context, driver: Driver) -> Layout:
    table = _read_table(driver, 12)

    const_end_offset = table[2]
    const_start_offset = driver.find_any(
        [b"nor0\x00", b"%llx:%d\x00"], 0, const_end_offset, 0x800, True
    )
    if not const_start_offset:
        raise AnalysisError("failed to find CONST start")

    const_start_offset = _align_down(const_start_offset, 0x10)
    const_start_addr = table[0] + const_start_offset
    const_end_addr = table[0] + const_end_offset

    text = Region(table[0], const_start_addr, 0)
    const = Region(const_start_addr, const_end_addr, const_start_offset)
    data = Region(table[4], table[5], const_end_offset)
    bss = Region(table[6], table[7])

    return Layout(text, const, data, bss)


def _detect_layout_v6823(context: Context, driver: Driver) -> Layout:
    table = _read_table(driver, 12)

    const_end_offset = table[2] - table[0]
    if context.app == App.IBOOT:
        const_end_offset = _align_down(const_end_offset, 0x4000)

    const_markers = (
        [b"virt_firmware\x00", b"double panic in\x00"]
        if context.app == App.AVPBOOTER
        else [
            b"nor0\x00",
            b"spi_nand0\x00",
            b"darwinos-ramdisk\x00",
        ]
    )

    const_start_offset = driver.find_any(const_markers, 0, const_end_offset, 0x4000)
    if not const_start_offset:
        raise AnalysisError("failed to find CONST start")

    const_start_offset = _align_up(const_start_offset, 0x10)
    const_start_addr = table[0] + const_start_offset
    const_end_addr = _align_up(table[2], 0x4000)

    text = Region(table[0], const_start_addr, 0)
    const = Region(const_start_addr, const_end_addr, const_start_offset)
    data = Region(
        const_end_addr if context.app == App.IBOOT else table[6],
        table[7],
        const_end_addr - table[0],
    )

    bss = Region(table[7], table[8])
    if bss.end < 0:
        # FIXME: Something weird going on here on newer iBoot, table has a
        # negative value that looks like a high memory VA.
        bss = None

    return Layout(text, const, data, bss)


VERSION_MIN = 1873


def analyze(driver: Driver) -> Layout:
    ctx = driver.detect_context()
    logging.info(f"Detected {ctx.app} version {ctx.version}.")

    if ctx.version.major < VERSION_MIN:
        raise UnsupportedVersionError(ctx.version)

    if ctx.version.major >= 6823:
        layout = _detect_layout_v6823(ctx, driver)
    else:
        layout = _detect_layout_v1585(ctx, driver)

    for name, region in layout.regions():
        logging.debug(f"Resolved region {name}: {region}")

    logging.info("Validating layout...")
    layout.validate()

    return layout
