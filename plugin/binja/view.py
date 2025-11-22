import sys
from pathlib import Path
from typing import override

from binaryninja import (
    Architecture,
    BinaryView,
    Platform,
    SectionSemantics,
    SegmentFlag,
    Symbol,
    SymbolType,
)

IBIS_PATH = Path(__file__).resolve().parent.parent.parent / "src"

if IBIS_PATH not in sys.path:
    sys.path.insert(0, str(IBIS_PATH))

from ibis.analyzer import analyze  # noqa: E402
from ibis.driver import Driver  # noqa: E402
from ibis.layout import Layout  # noqa: E402


class BinjaDriver(Driver):
    data: BinaryView

    def __init__(self, data: BinaryView) -> None:
        super().__init__()
        self.data = data

    @override
    def read(self, offset: int, size: int) -> bytes:
        return self.data.read(offset, size)


class IbisView(BinaryView):
    long_name: str | None = "iBoot"
    name: str | None = "iBoot"

    def __init__(self, parent_view: BinaryView):  # pyright: ignore[reportInconsistentConstructor]
        BinaryView.__init__(  # pyright: ignore[reportUnknownMemberType]
            self, file_metadata=parent_view.file, parent_view=parent_view
        )

    def _add_segment(
        self,
        name: str,
        data_offset: int | None,
        start: int,
        length: int,
        flags: int,
        semantics: SectionSemantics,
    ):
        length = min(length, 1 << 21)  # Cap segment size to prevent denial of service.
        data_length = 0 if data_offset is None else length

        # Conventionally, these should be auto segments/sections but since iBoot
        # can be a bit wonky, it's best to make them user segments so they can
        # be tweaked later without be clobbered on the next load.
        self.add_user_segment(start, length, data_offset or 0, data_length, flags)  # pyright: ignore[reportArgumentType]
        self.add_user_section(name, start, length, semantics)

    def _apply_layout(self, layout: Layout):
        self._add_segment(
            "TEXT",
            layout.text.file_offset,
            layout.text.start,
            layout.text.size,
            SegmentFlag.SegmentReadable | SegmentFlag.SegmentExecutable,
            SectionSemantics.ReadOnlyCodeSectionSemantics,
        )
        self._add_segment(
            "CONST",
            layout.const.file_offset,
            layout.const.start,
            layout.const.size,
            SegmentFlag.SegmentReadable,
            SectionSemantics.ReadOnlyDataSectionSemantics,
        )
        self._add_segment(
            "DATA",
            layout.data.file_offset,
            layout.data.start,
            layout.data.size,
            SegmentFlag.SegmentReadable | SegmentFlag.SegmentWritable,
            SectionSemantics.ReadWriteDataSectionSemantics,
        )
        if layout.bss:
            self._add_segment(
                "BSS",
                layout.bss.file_offset,
                layout.bss.start,
                layout.bss.size,
                SegmentFlag.SegmentReadable | SegmentFlag.SegmentWritable,
                SectionSemantics.ReadWriteDataSectionSemantics,
            )

    @classmethod
    def is_valid_for_data(cls, data: BinaryView) -> bool:
        try:
            BinjaDriver(data).detect_context()
            return True
        except Exception as e:
            print(e)
            return False

    @override
    def perform_get_address_size(self) -> int:
        return 8

    @override
    def init(self):
        if not self.parent_view:
            raise RuntimeError("Missing parent view")

        self.platform: Platform = Architecture["aarch64"].standalone_platform
        self.arch: Architecture = self.platform.arch

        driver = BinjaDriver(self.parent_view)
        layout = analyze(driver)

        self._apply_layout(layout)

        # Analysis can get confused about function bounds when if it fails to
        # detect no-return functions. A cheap hack is to create functions
        # starting at every PACIBSP, which shouldn't ever appear in the middle
        # of a function.
        for addr in range(layout.text.start, layout.text.end, 4):
            if self.read_int(addr, 4, False) == 0xD503237F:  # pacibsp
                self.add_function(addr)

        self.add_entry_point(layout.text.start)
        self.define_auto_symbol(
            Symbol(SymbolType.FunctionSymbol, layout.text.start, "_start")
        )

        return True
