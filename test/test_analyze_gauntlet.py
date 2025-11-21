from pathlib import Path

import pytest
from common import gauntlet_binaries

from ibis.analyzer import analyze
from ibis.driver import BinaryIODriver


@pytest.mark.parametrize("path", gauntlet_binaries(), ids=lambda p: str(p.name))
def test_gauntlet_binary(path: Path):
    with path.open("rb") as f:
        analyze(BinaryIODriver(f))
