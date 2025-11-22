import pytest

from ibis.context import (
    App,
    BannerParseError,
    TagParseError,
    UnsupportedAppError,
    Version,
    _parse_banner,
)


def test_parse_app():
    assert App.parse("SecureROM") == App.ROM
    assert App.parse("iBoot") == App.IBOOT
    assert App.parse("iBootStage2") == App.IBOOT

    with pytest.raises(UnsupportedAppError):
        App.parse("iBootStage3")
    with pytest.raises(UnsupportedAppError):
        App.parse("iBot")


def test_parse_version():
    assert Version("iBoot-3332.0.0.1.23").major == 3332
    assert Version("iBoot-6338.0.0.200.19").major == 6338

    with pytest.raises(TagParseError):
        Version("iBoot3332.0.0.1.23")
    with pytest.raises(TagParseError):
        Version("iBoot-abcd.0.0.1.23")
    with pytest.raises(TagParseError):
        Version("iBoot-.123")


def test_parse_banner():
    assert _parse_banner("SecureROM for t8110si, Copyright") == ("SecureROM", "t8110si")
    assert _parse_banner("iBootStage2 for t6030si, Copyright") == (
        "iBootStage2",
        "t6030si",
    )

    with pytest.raises(BannerParseError):
        _parse_banner("SecureROM per t8110si, Copyright")
    with pytest.raises(BannerParseError):
        _parse_banner("iBootStage2 di t6030si, Copyright")
    with pytest.raises(BannerParseError):
        _parse_banner("iBootfort6030si, Copyright")
