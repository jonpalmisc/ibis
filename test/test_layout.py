import pytest

from ibis.layout import Layout, MalformedLayoutError, MalformedRegionError, Region


def test_region_valid():
    region = Region(start=0x1000, end=0x2000)
    assert region.is_valid()


def test_region_invalid():
    region = Region(start=0x1000, end=0x1000)
    assert not region.is_valid()

    region = Region(start=0x2000, end=0x1000)
    assert not region.is_valid()


def test_region_compare():
    region_a = Region(start=0x1000, end=0x1FFF)
    region_b = Region(start=0x2000, end=0x3000)
    assert region_a < region_b

    region_a = Region(start=0x2000, end=0x3000)
    region_b = Region(start=0x2000, end=0x3000)
    assert region_b == region_a

    region_a = Region(start=0x2000, end=0x3000)
    region_b = Region(start=0x1000, end=0x1FFF)
    assert region_a > region_b

    region_a = Region(start=0x1000, end=0x2500)
    region_b = Region(start=0x2000, end=0x3000)
    assert not (region_a < region_b)


def test_layout_validate():
    layout = Layout(
        text=Region(start=0x1000, end=0x2000),
        const=Region(start=0x2000, end=0x3000),
        data=Region(start=0x3000, end=0x4000),
        bss=Region(start=0x4000, end=0x5000),
    )
    layout.validate()


def test_layout_validate_bad_region():
    with pytest.raises(MalformedRegionError):
        Layout(
            text=Region(start=0x1000, end=0x1000),  # Zero-size region
            const=Region(start=0x2000, end=0x3000),
            data=Region(start=0x3000, end=0x4000),
            bss=Region(start=0x4000, end=0x5000),
        ).validate()


def test_layout_validate_bad_layout():
    with pytest.raises(MalformedLayoutError):
        Layout(
            text=Region(start=0x1000, end=0x2500),  # Overlaps with CONST
            const=Region(start=0x2000, end=0x3000),
            data=Region(start=0x3000, end=0x4000),
            bss=Region(start=0x4000, end=0x5000),
        ).validate()
