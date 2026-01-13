import sys
import traceback
from collections.abc import Iterator
from pathlib import Path

import ida_auto
import ida_bytes
import ida_entry
import ida_funcs
import ida_ida
import ida_idaapi
import ida_idp
import ida_kernwin
import ida_loader
import ida_name
import ida_segment
import ida_strlist
import ida_xref

IBIS_PATH = Path(__file__).resolve().parent.parent.parent / "src"

if IBIS_PATH not in sys.path:
    sys.path.insert(0, str(IBIS_PATH))

from ibis.analyzer import analyze  # noqa: E402
from ibis.driver import Driver  # noqa: E402
from ibis.layout import FALLBACK_BSS_SIZE, Layout  # noqa: E402
from ibis.plugins import (  # noqa: E402
    ANALYZE_FAIL_MESSAGE,
    ERROR_HEADER,
    ISSUES_URL,
    MISSING_BSS_BOUNDS,
    PLEASE_REPORT_GUI_MESSAGE,
    PLEASE_REPORT_MESSAGE,
    POST_ANALYZE_FAIL_MESSAGE,
)
from ibis.strings import UNIQUE_STR_XREFS  # noqa: E402


def report_exception(message: str):
    print(f"\n{ERROR_HEADER}\n")
    print(f"{message}\n")
    print(traceback.format_exc())
    print(f"{PLEASE_REPORT_MESSAGE} ({ISSUES_URL})")

    ida_kernwin.warning(f"{message}\n\n{PLEASE_REPORT_GUI_MESSAGE}\n\n{ISSUES_URL}")


def string_info_decode(info: ida_strlist.string_info_t) -> str | None:
    content = ida_bytes.get_strlit_contents(info.ea, info.length, info.type)

    if content:
        try:
            return content.decode()
        except Exception:
            pass

    return None


def strings_containing(pattern: str) -> Iterator[ida_strlist.string_info_t]:
    info = ida_strlist.string_info_t()

    for i in range(ida_strlist.get_strlist_qty()):
        if not ida_strlist.get_strlist_item(info, i):
            continue

        decoded = string_info_decode(info)
        if decoded and pattern in decoded:
            yield info

            info = ida_strlist.string_info_t()  # New info object for next iteration.


def xrefs_to(ea: int) -> Iterator[ida_xref.xrefblk_t]:
    xref = ida_xref.xrefblk_t()

    # This might bite us later if we don't limit it to code references.
    if xref.first_to(ea, ida_xref.XREF_ALL):
        yield xref

        while xref.next_to():
            yield xref


def set_name_from_str_xref(name: str, pattern: str) -> ida_funcs.func_t | None:
    if not (needle := next(strings_containing(pattern), None)):
        return None

    if not (ref := next(xrefs_to(needle.ea), None)):
        return None

    if not (func := ida_funcs.get_func(ref.frm)):
        return None

    ida_name.set_name(func.start_ea, name)
    return func


class PostProcessHook(ida_idp.IDB_Hooks):
    def __init__(self):
        super().__init__()

    def auto_empty_finally(self, *args):
        try:
            panic = set_name_from_str_xref("_panic", "double panic in")
            if not panic:
                raise ValueError("Failed to find panic function")

            panic.flags |= ida_funcs.FUNC_NORET
            ida_funcs.update_func(panic)

            for name, needle in UNIQUE_STR_XREFS.items():
                set_name_from_str_xref(name, needle)

        except Exception:
            report_exception(POST_ANALYZE_FAIL_MESSAGE)

        ida_auto.auto_wait()


POST_PROCESS_HOOK: PostProcessHook | None = None


input_size = None  # XXX: Global, set in `load_file`.


def add_segment(
    fd, name: str, file_offset: int | None, ea: int, size: int, type: str, perm: int
):
    if file_offset is not None and input_size:
        size = min(size, input_size - file_offset)
        fd.file2base(file_offset, ea, ea + size, ida_loader.FILEREG_PATCHABLE)

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

    bss_start = layout.bss.start if layout.bss else layout.data.end
    bss_size = layout.bss.size if layout.bss else FALLBACK_BSS_SIZE

    if not layout.bss:
        print(MISSING_BSS_BOUNDS)

    add_segment(
        fd,
        "BSS",
        None,
        bss_start,
        bss_size,
        "BSS",
        ida_segment.SEGPERM_READ | ida_segment.SEGPERM_WRITE,
    )


class IDADriver(Driver):
    def __init__(self, fd) -> None:
        super().__init__()
        self.fd = fd

    # @override
    def read(self, offset: int, size: int) -> bytes:
        self.fd.seek(offset)
        return self.fd.read(size)

    def size(self) -> int:
        self.fd.seek(0, ida_idaapi.SEEK_END)
        return self.fd.tell()


def accept_file(fd, _):
    try:
        ctx = IDADriver(fd).detect_context()

        return {"format": f"{ctx.app.value}", "processor": "arm"}
    except Exception as e:
        print(e)

    return 0


def load_file(fd, neflags: int, _):
    ida_idp.set_processor_type("arm", ida_idp.SETPROC_LOADER)
    ida_ida.inf_set_app_bitness(64)

    if (neflags & ida_loader.NEF_RELOAD) != 0:
        return 1

    fd.seek(0, ida_idaapi.SEEK_END)

    global input_size
    input_size = fd.tell()

    try:
        layout = analyze(IDADriver(fd))
        apply_layout(fd, layout)

        # Analysis can get confused about function bounds when if it fails to detect
        # no-return functions. A cheap hack is to create functions starting at every
        # PACIBSP, which shouldn't ever appear in the middle of a function.
        for addr in range(layout.text.end - 4, layout.text.start - 4, -4):
            if ida_bytes.get_dword(addr) == 0xD503237F:  # pacibsp
                print(f"Adding function @ {addr:#x}...")
                ida_funcs.add_func(addr)

        start = layout.text.start

    except Exception:
        report_exception(ANALYZE_FAIL_MESSAGE)

        add_segment(
            fd,
            "APP",
            0,
            0,
            input_size,
            "CODE",
            ida_segment.SEGPERM_READ
            | ida_segment.SEGPERM_WRITE
            | ida_segment.SEGPERM_EXEC,
        )

        start = 0

    ida_entry.add_entry(0, start, "_start", True)

    global POST_PROCESS_HOOK
    POST_PROCESS_HOOK = PostProcessHook()
    POST_PROCESS_HOOK.hook()

    return 1
