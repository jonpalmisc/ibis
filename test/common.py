import logging
from collections.abc import Generator
from pathlib import Path

CORPUS_PATH = Path(__file__).parent.parent / "corpus"


def open_corpus_binary(name: str):
    """Open a binary from the corpus."""

    logging.info(f"Loading corpus binary: {name}")  # Make output in tests nicer.
    return (CORPUS_PATH / name).open("rb")


def gauntlet_binaries() -> Generator[Path]:
    return (CORPUS_PATH / "gauntlet").iterdir()
