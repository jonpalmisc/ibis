#!/usr/bin/env python3

import json
import logging
import subprocess
import tempfile
from argparse import ArgumentParser, HelpFormatter
from functools import partial
from itertools import chain
from multiprocessing import Pool
from pathlib import Path


def exec(cmd: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(cmd, capture_output=True, cwd=cwd)
    result.check_returncode()
    return result.stdout.decode().strip()


def fetch_version_urls(version: str, devices: list[str]):
    urls = []

    for device in devices:
        try:
            output = exec(
                [
                    "ipsw",
                    "download",
                    "ipsw",
                    "--version",
                    version,
                    "--device",
                    device,
                    "--urls",
                ]
            )
            urls += [line for line in output.splitlines()]
        except Exception:
            logging.warning(
                f"Failed to get URLs for device/version: {device}/{version}"
            )

    return urls


def extract_im4p(path: Path, tag: str, output_dir: Path) -> Path:
    output = output_dir / f"{tag}-{path.stem}"

    logging.debug(f"Extracting IM4P: {path}")
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
    parser = ArgumentParser(
        formatter_class=lambda prog: HelpFormatter(prog, max_help_position=44)
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="output directory",
    )
    parser.add_argument(
        "-d",
        "--device",
        metavar="DEVICE",
        dest="devices",
        action="append",
        help="device(s) to fetch iBoots for (can be passed multiple times)",
    )
    parser.add_argument(
        "-v",
        "--version",
        metavar="VERSION",
        dest="versions",
        action="append",
        help="iOS version(s) to fetch iBoots for (can be passed multiple times)",
    )
    parser.add_argument(
        "-V",
        "--verbose",
        action="store_true",
        help="enable verbose output",
    )
    parser.add_argument(
        "-D",
        "--default",
        action="store_true",
        help="use the default device & version spread",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=8,
        help="number of download/worker jobs to use (default: 8)",
    )

    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if args.default:
        logging.info("Using default config...")

        args.versions = ["18.0", "18.2", "18.4", "18.6", "26.0", "26.1"]
        args.devices = [
            "iPhone11,8",  # A12, PAC
            "iPhone14,2",  # A15, SPTM/TXM
            "iPhone17,1",  # A18, Exclaves
            "iPhone18,1",  # A19, MTE
            "iPad13,5",  # M1
            "iPad17,3",  # M5, Exclaves
        ]

        logging.info(f"Version set: {args.versions}")
        logging.info(f"Device set:  {args.devices}")

    if not args.versions:
        raise ValueError("no versions provided")
    if not args.devices:
        raise ValueError("no devices provided")

    logging.info(f"Using {args.jobs} threads...")

    with Pool(args.jobs) as p:
        url_groups = p.map(
            partial(fetch_version_urls, devices=args.devices), args.versions
        )
    urls = list(chain(*url_groups))

    logging.info(f"Found {len(urls)} URLs.")

    with Pool(args.jobs) as p:
        p.map(partial(download_iboot, output_dir=args.output), urls)
