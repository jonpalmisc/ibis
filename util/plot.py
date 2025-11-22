#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path

from ibis.context import App
from ibis.driver import BinaryIODriver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", type=Path, help="directory to process")
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

    rom_map = {}
    iboot_map = {}
    for path in args.dir.glob("**/*"):
        if not path.is_file():
            continue

        with path.open("rb") as f:
            logging.debug(f"Processing file: {path}")

            driver = BinaryIODriver(f)
            try:
                ctx = driver.detect_context()
            except Exception:
                print(f"Failed to detect context for file: {path}")
                raise

            if ctx.app == App.ROM:
                if ctx.version not in rom_map:
                    rom_map[ctx.version.major] = []

                rom_map[ctx.version.major].append(f"{ctx.target}")
            else:
                if ctx.version not in iboot_map:
                    iboot_map[ctx.version.major] = []

                iboot_map[ctx.version.major].append(f"{ctx.target}")

    all_versions = sorted(set(list(rom_map.keys()) + list(iboot_map.keys())))

    print("Version,SecureROM,iBoot")
    for v in all_versions:
        rom_target = rom_map[v][0] if v in rom_map else ""
        iboot_target = iboot_map[v][0] if v in iboot_map else ""

        print(f"{v},{rom_target},{iboot_target}")


if __name__ == "__main__":
    main()
