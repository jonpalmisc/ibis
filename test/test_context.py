import pytest

from ibis.context import App, TagParseError, UnsupportedAppError, version_from_tag


def test_app_from_banner():
    assert App.from_banner("SecureROM for t8110si, Copyright") == App.ROM
    assert App.from_banner("iBoot for t8015si, Copyright") == App.IBOOT
    assert App.from_banner("iBootStage2 for t6030si, Copyright") == App.IBOOT


def test_app_from_invalid():
    with pytest.raises(UnsupportedAppError):
        App.from_banner("FooROM for t8110si, Copyright")
    with pytest.raises(UnsupportedAppError):
        App.from_banner("iBot for t8015si, Copyright")
    with pytest.raises(UnsupportedAppError):
        App.from_banner("iBootStage3 for t6030si, Copyright")


def test_version_from_tag():
    assert version_from_tag("iBoot-3332.0.0.1.23") == 3332
    assert version_from_tag("iBoot-6338.0.0.200.19") == 6338


def test_version_from_tag_invalid():
    with pytest.raises(TagParseError):
        version_from_tag("iBoot3332.0.0.1.23")
    with pytest.raises(TagParseError):
        version_from_tag("iBoot-abcd.0.0.1.23")
    with pytest.raises(TagParseError):
        version_from_tag("iBoot-.123")
