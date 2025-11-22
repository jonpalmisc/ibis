#!/usr/bin/env python3

import argparse
import csv
import sys
from itertools import chain
from pathlib import Path

from ibis.context import App
from ibis.driver import BinaryIODriver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", type=Path, help="directory to process")

    args = parser.parse_args()

    if not args.dir.exists() or not args.dir.is_dir():
        raise ValueError("input directory is missing or not a directory")

    map: dict[App, dict[int, set[str]]] = {}
    for path in args.dir.glob("**/*"):
        if not path.is_file():
            continue

        with path.open("rb") as f:
            driver = BinaryIODriver(f)
            try:
                ctx = driver.detect_context()
            except Exception:
                print(f"Failed to detect context for file: {path}")
                raise

            if ctx.app not in map:
                map[ctx.app] = {}
            if ctx.version.major not in map[ctx.app]:
                map[ctx.app][ctx.version.major] = set()

            map[ctx.app][ctx.version.major].add(ctx.target)

    all_apps = map.keys()
    all_versions = sorted(chain.from_iterable([map[app].keys() for app in map]))

    writer = csv.writer(sys.stdout)

    writer.writerow(["Version"] + [str(app) for app in map])
    for ver in all_versions:
        row = [str(ver)]

        row.extend(
            "\n".join(map[app][ver]) if ver in map[app] else "" for app in all_apps
        )

        writer.writerow(row)


if __name__ == "__main__":
    main()
