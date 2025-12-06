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
    """
    Read the "layout table" embedded in the binary, which contains some helpful
    region information.

    Earlier versions of the layout table with pointers to the banner/tag strings
    will automatically have the first 3 elements (string pointers) removed.
    """

    table = [
        struct.unpack("q", driver.read(_LAYOUT_TABLE_OFFSET + (i * 8), 8))[0]
        for i in range(count)
    ]

    if table[0] & 0xFFF != 0:
        logging.debug("Ignoring first 3 elements of layout table... (old format)")
        table = table[3:]

    # for i in range(len(table)):
    #     logging.debug(f"table[{i}] = {table[i]:#x}")

    return table


def _detect_layout_v1585(context: Context, driver: Driver) -> Layout:
    """
    Detect the layout of images newer than major verison 1585.
    """

    # The table format on this version is as follows:
    #
    #   0: TEXT Start
    #      ...
    #   2: CONST End Offset
    #      ...
    #   4: DATA Start
    #   5: DATA End
    #   6: BSS Start
    #   7: BSS End
    #
    table = _read_table(driver, 12)

    const_end_offset = table[2]

    # The end of TEXT and start of CONST is not explicitly defined in the table,
    # but the two strings below reliably appear at the start of CONST and can be
    # used to locate the segment boundary.
    const_start_offset = driver.find_any(
        [
            b"arch_get_cluster_id\x00",
            b"arch_vtop\x00",
            b"arch_get_virt_address_bits\x00",
            b"nor0\x00",
            b"%llx:%d\x00",
        ],
        0,
        const_end_offset,
        0x800,
        True,
    )
    if not const_start_offset:
        raise AnalysisError("failed to find CONST start")

    # The strings sometimes land at an unaligned addres though; round down.
    const_start_offset = _align_down(const_start_offset, 0x10)

    const_start_addr = table[0] + const_start_offset
    const_end_addr = table[0] + const_end_offset

    text = Region(table[0], const_start_addr, 0)
    const = Region(const_start_addr, const_end_addr, const_start_offset)

    # DATA should always start at a page boundary, but the page size is not the
    # same on all devices...
    data_start_offset = _align_up(const_end_offset, 0x1000)

    # As a cheap hack to avoid keeping a mapping of target to page size, we can
    # try first rounding up to a 4K page and reading the following page. If the
    # page is full of zeroes, then we are probably still within the segment
    # padding and should round up to the 16K boundary instead.
    data_first_4k = driver.read(data_start_offset, 0x1000)
    if all(b == 0 for b in data_first_4k):
        data_start_offset = _align_up(data_start_offset, 0x4000)

    data = Region(table[4], table[5], data_start_offset)
    bss = Region(table[6], table[7])

    return Layout(text, const, data, bss)


def _detect_layout_v6823(context: Context, driver: Driver) -> Layout:
    """
    Detect the layout of images newer than major verison 6823.
    """

    # The table format on this version is as follows:
    #
    #   0: TEXT Start
    #      ...
    #   2: CONST End
    #      ...
    #   6: DATA Start
    #   7: DATA End / BSS Start
    #   8: BSS End
    #
    table = _read_table(driver, 12)

    # CONST end is stored as an address in these newer versions, but we can rely
    # on it being contiguous with TEXT, so just take the difference from TEXT
    # start to get the file offset.
    const_end_offset = table[2] - table[0]

    if context.app == App.IBOOT:
        # I can't remember when or why I added this, but the reported segment
        # end must have been too far in some instances and aligning downwards
        # fixed it.
        const_end_offset = _align_down(const_end_offset, 0x4000)

    # Use string heuristics again (see function above), but with updated strings
    # for newer images.
    const_start_offset = driver.find_any(
        (
            # AVPBooter has different strings.
            [b"virt_firmware\x00", b"double panic in\x00"]
            if context.app == App.AVP_BOOTER
            else [
                b"%llx:%d\x00",
                b"anc_firmware\x00",
                b"nor0\x00",
                b"spi_nand0\x00",
                b"darwinos-ramdisk\x00",
            ]
        ),
        0,
        const_end_offset,
        0x4000,
    )
    if not const_start_offset:
        raise AnalysisError("failed to find CONST start")

    const_start_offset = _align_down(const_start_offset, 0x10)
    const_start_addr = table[0] + const_start_offset

    const_end_offset = _align_up(table[2] - table[0], 0x1000)

    # See explanation in function above; we need to guess the page size.
    data_first_4k = driver.read(const_end_offset, 0x1000)
    if all(b == 0 for b in data_first_4k):
        const_end_offset = _align_up(const_end_offset, 0x4000)

    const_end_addr = table[0] + const_end_offset

    text = Region(table[0], const_start_addr, 0)
    const = Region(const_start_addr, const_end_addr, const_start_offset)
    data = Region(
        const_end_addr if context.app.is_iboot() else table[6],
        table[7],
        const_end_addr - table[0],
    )

    bss = Region(table[7], table[8])
    if bss.end < 0:
        # FIXME: Something weird going on here on newer iBoot, table has a
        # negative value that looks like a high memory VA.
        bss = None

    return Layout(text, const, data, bss)


VERSION_MIN = 1585  # Earliest 64-bit ROM (A7)


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
