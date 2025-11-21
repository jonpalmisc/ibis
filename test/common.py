import logging
from pathlib import Path

CORPUS_PATH = Path(__file__).parent.parent / "corpus"


def corpus_binary(name: str):
    """Open a binary from the corpus."""

    logging.info(f"Loading corpus binary: {name}")  # Make output in tests nicer.
    return (CORPUS_PATH / name).open("rb")
