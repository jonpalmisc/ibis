from io import BytesIO

from ibis.driver import BinaryIODriver


def test_driver_read_basic():
    bio = BytesIO(b"A" * 8 + b"B" * 8)
    driver = BinaryIODriver(bio)

    assert driver.read(4, 8) == b"AAAABBBB"


def test_driver_read_str():
    bio = BytesIO(b"\xff" * 8 + b"Hello, world!\x00" + b"\xff" * 8)
    driver = BinaryIODriver(bio)

    assert driver.read_str(8, 16) == "Hello, world!"
    assert driver.read_str(8, 5) == "Hello"
