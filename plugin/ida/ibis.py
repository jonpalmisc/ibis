import sys
from pathlib import Path
from typing import override

import ida_bytes
import ida_entry
import ida_funcs
import ida_ida
import ida_idp
import ida_loader
import ida_segment

IBIS_PATH = Path(__file__).resolve().parent.parent.parent / "src"

if IBIS_PATH not in sys.path:
    sys.path.insert(0, str(IBIS_PATH))

from ibis.analyzer import analyze  # noqa: E402
from ibis.driver import Driver  # noqa: E402
from ibis.layout import Layout  # noqa: E402


class IDADriver(Driver):
    def __init__(self, fd) -> None:
        super().__init__()
        self.fd = fd

    @override
    def read(self, offset: int, size: int) -> bytes:
        self.fd.seek(offset)
        return self.fd.read(size)


def accept_file(fd, _):
    try:
        ctx = IDADriver(fd).detect_context()

        return {"format": f"{ctx.app.value}", "processor": "arm"}
    except Exception as e:
        print(e)

    return 0


def add_segment(
    fd, name: str, file_offset: int | None, ea: int, size: int, type: str, perm: int
):
    if file_offset is not None:
        fd.file2base(file_offset, ea, ea + size, False)

    segm = ida_segment.segment_t()
    segm.bitness = 2  # 64-bit
    segm.start_ea = ea
    segm.end_ea = ea + size

    ida_segment.add_segm_ex(segm, name, type, ida_segment.ADDSEG_OR_DIE)

    ida_segment.set_segm_class(segm, type)
    segm.perm = perm

    ida_segment.update_segm(segm)


def apply_layout(fd, layout: Layout):
    add_segment(
        fd,
        "TEXT",
        layout.text.file_offset,
        layout.text.start,
        layout.text.size,
        "CODE",
        ida_segment.SEGPERM_READ | ida_segment.SEGPERM_EXEC,
    )
    add_segment(
        fd,
        "CONST",
        layout.const.file_offset,
        layout.const.start,
        layout.const.size,
        "DATA",
        ida_segment.SEGPERM_READ,
    )
    add_segment(
        fd,
        "DATA",
        layout.data.file_offset,
        layout.data.start,
        layout.data.size,
        "DATA",
        ida_segment.SEGPERM_READ | ida_segment.SEGPERM_WRITE,
    )
    if layout.bss:
        add_segment(
            fd,
            "BSS",
            layout.bss.file_offset,
            layout.bss.start,
            layout.bss.size,
            "BSS",
            ida_segment.SEGPERM_READ | ida_segment.SEGPERM_WRITE,
        )


def load_file(fd, neflags: int, _):
    ida_idp.set_processor_type("arm", ida_idp.SETPROC_LOADER)
    ida_ida.inf_set_app_bitness(64)

    if (neflags & ida_loader.NEF_RELOAD) != 0:
        return 1

    layout = analyze(IDADriver(fd))
    apply_layout(fd, layout)

    # Analysis can get confused about function bounds when if it fails to detect
    # no-return functions. A cheap hack is to create functions starting at every
    # PACIBSP, which shouldn't ever appear in the middle of a function.
    for addr in range(layout.text.start, layout.text.end, 4):
        if ida_bytes.get_dword(addr) == 0xD503237F:  # pacibsp
            print(f"Adding function @ {addr:#x}...")
            ida_funcs.add_func(addr)

    ida_entry.add_entry(0, layout.text.start, "_start", True)

    return 1
