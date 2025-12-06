from common import open_corpus_binary

from ibis.analyzer import analyze
from ibis.driver import BinaryIODriver
from ibis.layout import Region


def test_rom_v1873_t7000si_30cd00a():
    with open_corpus_binary("SecureROM-1873.0.0.1.19-t7000si-30cd00a") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000000, 0x100015080, 0)
        assert layout.const == Region(0x100015080, 0x100017E70, 0x15080)
        # assert layout.rodata == Region(0x100017E70, 0x100018630, 0x17E70)
        assert layout.data == Region(0x180080000, 0x1800807C0, 0x18000)
        assert layout.bss == Region(0x1800807C0, 0x180087AA0)


def test_rom_v2234_s8003si_bad3102():
    with open_corpus_binary("SecureROM-2234.0.0.2.22-s8003si-bad3102") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000000, 0x100015580, 0)
        assert layout.const == Region(0x100015580, 0x1000185CC, 0x15580)
        assert layout.data == Region(0x180080000, 0x180080840, 0x19000)
        assert layout.bss == Region(0x180080840, 0x180088368)


def test_rom_v3332_t8015si_af56128():
    with open_corpus_binary("SecureROM-3332.0.0.1.23-t8015si-af56128") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000000, 0x100017240, 0)
        assert layout.const == Region(0x100017240, 0x10001B988, 0x17240)
        # assert layout.rodata == Region(0x10001B988, 0x10001CA88, 0x1B988)
        assert layout.data == Region(0x180000000, 0x180001100, 0x1C000)
        assert layout.bss == Region(0x180001100, 0x180009FB8)


def test_rom_v4479_t8030_7f8eca4():
    with open_corpus_binary("SecureROM-4479.0.0.100.4-t8030si-7f8eca4") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000000, 0x10001EBC0, 0)
        assert layout.const == Region(0x10001EBC0, 0x100025390, 0x1EBC0)
        # assert layout.rodata == Region(0x10001B988, 0x10001CA88, 0x1B988)
        assert layout.data == Region(0x19C00C000, 0x19C00D100, 0x28000)
        assert layout.bss == Region(0x19C00D100, 0x19C014060)


def test_rom_v6338_t8110si_08c48dc():
    with open_corpus_binary("SecureROM-6338.0.0.200.19-t8110si-08c48dc") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000000, 0x1000286C0, 0)
        assert layout.const == Region(0x1000286C0, 0x1000309A8, 0x286C0)
        # assert layout.rodata == Region(0x1000309A8, 0x100031028, 0x309A8)
        assert layout.data == Region(0x1FC00C000, 0x1FC00C680, 0x34000)
        assert layout.bss == Region(0x1FC00C680, 0x1FC028081)


def test_rom_v8104_t8130si_2e19fc4():
    with open_corpus_binary("SecureROM-8104.0.0.201.4-t8130si-2e19fc4") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000000, 0x100057BC0, 0)
        assert layout.const == Region(0x100057BC0, 0x10005C000, 0x57BC0)
        # assert layout.rodata == Region(0x10005C000, 0x10005D000, 0x5C000)
        assert layout.data == Region(0x1FC038000, 0x1FC039000, 0x5C000)
        assert layout.bss == Region(0x1FC039000, 0x1FC048C40)


def test_iboot_v4513_j317_e755528():
    with open_corpus_binary("iBoot-4513.200.204.100.6-j317-e755528") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x19C030000, 0x19C0A8A00, 0)
        assert layout.const == Region(0x19C0A8A00, 0x19C0E34C8, 0x78A00)
        assert layout.data == Region(0x19C0E4000, 0x19C1AAF40, 0xB4000)
        assert layout.bss == Region(0x19C1AAF40, 0x19C1CC0E0)


def test_iboot_v6723_n104_fbbc050():
    with open_corpus_binary("iBoot-6723.42.3-n104-fbbc050") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x19C030000, 0x19C160280, 0)
        assert layout.const == Region(0x19C160280, 0x19C16D160, 0x130280)
        assert layout.data == Region(0x19C170000, 0x19C2ADB00, 0x140000)
        assert layout.bss == Region(0x19C2ADB00, 0x19C2D42A2)


def test_iboot_v8419_d421_8fdff04():
    with open_corpus_binary("iBoot-8419.0.42.112.1-d421-8fdff04") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x19C050000, 0x19C14C100, 0)
        assert layout.const == Region(0x19C14C100, 0x19C1F4000, 0xFC100)
        assert layout.data == Region(0x19C1F4000, 0x19C2BD240, 0x1A4000)
        assert layout.bss == Region(0x19C2BD240, 0x19C2E5C40)


def test_iboot_v11881_n841_edb2ea9():
    with open_corpus_binary("iBoot-11881.140.96-n841-edb2ea9") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x19C050000, 0x19C14A040, 0)
        assert layout.const == Region(0x19C14A040, 0x19C198000, 0xFA040)
        assert layout.data == Region(0x19C198000, 0x19C25F480, 0x148000)
        assert layout.bss == Region(0x19C25F480, 0x19C2837B0)


def test_iboot_v13822_v53_ff63963():
    with open_corpus_binary("iBoot-13822.42.2-v53-ff63963") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x1FC08C000, 0x1FC3DDA40, 0)
        assert layout.const == Region(0x1FC3DDA40, 0x1FC3EC000, 0x351A40)
        assert layout.data == Region(0x1FC3EC000, 0x1FC47C680, 0x360000)
        assert layout.bss is None


def test_stage1_v3319_d11_e919da8():
    with open_corpus_binary("iBootStage1-3319.0.0.1.9-d11-e919da8") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x1800B0000, 0x1800DFEC0, 0)
        assert layout.const == Region(0x1800DFEC0, 0x1800F14F4, 0x2FEC0)
        assert layout.data == Region(0x1800F4000, 0x1800F5C00, 0x44000)
        assert layout.bss == Region(0x1800F5C00, 0x18010DCFC)


def test_stage1_v7459_ipad5_807e588():
    with open_corpus_binary("iBootStage1-7459.140.15-ipad5-807e588") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x180380000, 0x1803AB9C0, 0)
        assert layout.const == Region(0x1803AB9C0, 0x1803B2000, 0x2B9C0)
        assert layout.data == Region(0x1803B2000, 0x1803B2A00, 0x32000)
        assert layout.bss == Region(0x1803B2A00, 0x1803BD0F8)


def test_avp_v7459_vmapple2_ae20f87():
    with open_corpus_binary("AVPBooter-7459.101.2-vmapple2-ae20f87") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000, 0x126FC0, 0)
        assert layout.const == Region(0x126FC0, 0x128000, 0x26FC0)
        assert layout.data == Region(0x70028000, 0x70028280, 0x28000)
        assert layout.bss == Region(0x70028280, 0x7002C088)


def test_avp_v10151_vmapple2_a1face9():
    with open_corpus_binary("AVPBooter-10151.121.1-vmapple2-a1face9") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000, 0x132040, 0)
        assert layout.const == Region(0x132040, 0x134000, 0x32040)
        assert layout.data == Region(0x70028000, 0x70028780, 0x34000)
        assert layout.bss == Region(0x70028780, 0x700340F8)


def test_avp_v11881_vresearch1_36f5148():
    with open_corpus_binary("AVPBooter-11881.81.2-vresearch1-36f5148") as f:
        layout = analyze(BinaryIODriver(f))

        assert layout.text == Region(0x100000, 0x1369C0, 0)
        assert layout.const == Region(0x1369C0, 0x138000, 0x369C0)
        assert layout.data == Region(0x70028000, 0x70028F40, 0x38000)
        assert layout.bss == Region(0x70028F40, 0x700340F8)
