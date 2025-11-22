#!/usr/bin/env python3

import argparse
import logging
from hashlib import sha256
from pathlib import Path

from ibis.driver import BinaryIODriver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", type=Path, help="directory to process")
    parser.add_argument(
        "-d", "--dry-run", action="store_true", help="show (but don't perform) renames"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
        )

    if not args.dir.exists() or not args.dir.is_dir():
        raise ValueError("input directory is missing or not a directory")

    for path in args.dir.iterdir():
        if not path.is_file():
            continue

        with path.open("rb") as f:
            logging.debug(f"Processing file: {path}")

            shorthash = sha256(f.read()).hexdigest()[:7]

            driver = BinaryIODriver(f)
            ctx = driver.detect_context()

            new_name = f"{ctx.app}-{ctx.version}-{ctx.target}-{shorthash}"
            print(f"{path.name} -> {new_name}")

            new_path = path.parent / new_name
            if not args.dry_run:
                path.rename(new_path)


if __name__ == "__main__":
    main()
