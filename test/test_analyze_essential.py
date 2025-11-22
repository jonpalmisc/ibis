from common import open_corpus_binary

from ibis.analyzer import analyze
from ibis.driver import BinaryIODriver
from ibis.layout import Region


def test_rom_v1873_t7000si():
    with open_corpus_binary("SecureROM-1873.0.0.1.19-t7000si") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000000, 0x100015080, 0)
        assert layout.const == Region(0x100015080, 0x100017E70, 0x15080)
        # assert layout.rodata == Region(0x100017E70, 0x100018630, 0x17E70)
        assert layout.data == Region(0x180080000, 0x1800807C0, 0x17E70)
        assert layout.bss == Region(0x1800807C0, 0x180087AA0)


def test_rom_v3332_t8015si():
    with open_corpus_binary("SecureROM-3332.0.0.1.23-t8015si") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000000, 0x100017240, 0)
        assert layout.const == Region(0x100017240, 0x10001B988, 0x17240)
        # assert layout.rodata == Region(0x10001B988, 0x10001CA88, 0x1B988)
        assert layout.data == Region(0x180000000, 0x180001100, 0x1B988)
        assert layout.bss == Region(0x180001100, 0x180009FB8)


def test_rom_v6338_t8110si():
    with open_corpus_binary("SecureROM-6338.0.0.200.19-t8110si") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000000, 0x1000286C0, 0)
        assert layout.const == Region(0x1000286C0, 0x1000309A8, 0x286C0)
        # assert layout.rodata == Region(0x1000309A8, 0x100031028, 0x309A8)
        assert layout.data == Region(0x1FC00C000, 0x1FC00C680, 0x309A8)
        assert layout.bss == Region(0x1FC00C680, 0x1FC028081)


def test_rom_v8104_t8130si():
    with open_corpus_binary("SecureROM-8104.0.0.201.4-t8130si") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000000, 0x100057BC0, 0)
        assert layout.const == Region(0x100057BC0, 0x10005C000, 0x57BC0)
        # assert layout.rodata == Region(0x10005C000, 0x10005D000, 0x5C000)
        assert layout.data == Region(0x1FC038000, 0x1FC039000, 0x5C000)
        assert layout.bss == Region(0x1FC039000, 0x1FC048C40)


def test_iboot_v8419_d421ap():
    with open_corpus_binary("iBoot-8419.0.42.112.1-d421ap.RELEASE") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x19C050000, 0x19C14C100, 0)
        assert layout.const == Region(0x19C14C100, 0x19C1F4000, 0xFC100)
        assert layout.data == Region(0x19C1F4000, 0x19C2BD240, 0x1A4000)
        assert layout.bss == Region(0x19C2BD240, 0x19C2E5C40)


def test_illb_v11881_n841ap():
    with open_corpus_binary("iLLB-11881.140.96-n841ap.RELEASE") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x19C050000, 0x19C14A040, 0)
        assert layout.const == Region(0x19C14A040, 0x19C198000, 0xFA040)
        assert layout.data == Region(0x19C198000, 0x19C25F480, 0x148000)
        assert layout.bss == Region(0x19C25F480, 0x19C2837B0)


def test_iboot_v13822_v53ap():
    with open_corpus_binary("iBoot-13822.42.2-v53ap.RELEASE") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x1FC08C000, 0x1FC3DDA40, 0)
        assert layout.const == Region(0x1FC3DDA40, 0x1FC3EC000, 0x351A40)
        assert layout.data == Region(0x1FC3EC000, 0x1FC47C680, 0x360000)
        assert layout.bss is None
