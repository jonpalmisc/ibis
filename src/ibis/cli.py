import json
from argparse import ArgumentParser
from pathlib import Path

from ibis.analyzer import analyze
from ibis.driver import BinaryIODriver
from ibis.layout import Layout, Region


def _print_region(name: str, region: Region):
    file_span = (
        f"{region.file_offset:#08x}-{region.file_offset + region.size:#08x}"
        if region.file_offset is not None
        else ""
    )
    addr_span = f"{region.start:#08x}-{region.end:#x}"

    print(f"{name:<12s}{addr_span:<28}{file_span:<24}{region.size:#08x}")


def _print_layout(layout: Layout):
    _print_region("TEXT", layout.text)
    _print_region("CONST", layout.const)
    _print_region("DATA", layout.data)
    if layout.bss:
        _print_region("BSS", layout.bss)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "input", type=Path, help="input to analyze (iBoot family binary)"
    )
    parser.add_argument("-j", "--json", action="store_true", help="emit output as JSON")

    args = parser.parse_args()

    with args.input.open("rb") as f:
        driver = BinaryIODriver(f)

        context = driver.detect_context()
        layout = analyze(driver)

        if args.json:
            regions_json = {}
            for name, region in layout.regions():
                regions_json[name] = {
                    "offset": region.file_offset,
                    "size": region.size,
                    "start": region.start,
                    "end": region.end,
                }

            output_json = {
                "app": str(context.app),
                "version": str(context.version),
                "target": context.target,
                "regions": regions_json,
            }

            print(json.dumps(output_json))
        else:
            print(f"{context.app}/{context.version}/{context.target}\n")
            _print_layout(layout)
