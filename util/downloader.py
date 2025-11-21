#!/usr/bin/env python3

import json
import subprocess
import tempfile
from argparse import ArgumentParser
from functools import partial
from itertools import chain
from multiprocessing import Pool
from pathlib import Path


def exec(cmd: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(cmd, capture_output=True, cwd=cwd)
    result.check_returncode()
    return result.stdout.decode().strip()


def fetch_version_urls(version: str):
    output = exec(["ipsw", "download", "ipsw", "--version", version, "--urls"])
    return [line for line in output.splitlines()]


def extract_im4p(path: Path, tag: str, output_dir: Path) -> Path:
    output = output_dir / f"{tag}-{path.stem}"

    exec(
        [
            "ipsw",
            "img4",
            "im4p",
            "extract",
            "--no-color",
            "--output",
            str(output),
            str(path),
        ]
    )

    return output


IGNORE_PATTERNS = ["sep-firmware", "iBootData"]


def download_iboot(url: str, output_dir: Path):
    info_json = exec(
        ["ipsw", "info", "--json", "--remote", url],
    )
    info = json.loads(info_json)

    tag = f"{info['version']}-{info['build']}"

    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        paths_json = exec(
            ["ipsw", "extract", "--json", "--iboot", "--remote", url], cwd=d
        )
        for path in json.loads(paths_json):
            if any(p in path for p in IGNORE_PATTERNS):
                continue

            payload_path = extract_im4p(d / path, tag, output_dir)
            print(payload_path)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="output directory",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=8,
        help="number of download/worker jobs to use (default: 8)",
    )
    parser.add_argument(
        "-v",
        "--version",
        dest="versions",
        action="append",
        help="iOS version to fetch (can be passed multiple times)",
    )

    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    if not args.versions:
        raise ValueError("no versions to download provided")

    with Pool(args.jobs) as p:
        url_groups = p.map(fetch_version_urls, args.versions)
    urls = list(chain(*url_groups))

    with Pool(args.jobs) as p:
        p.map(partial(download_iboot, output_dir=args.output), urls)
