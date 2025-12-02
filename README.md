# Ibis

Ibis is a Python library with accompanying disassembler plugins for analyzing
64-bit iBoot-like firmware, e.g. SecureROM, iBoot, AVPBooter, etc.

The primary goal of Ibis is to provide **accurate memory layout information**
for a wide range of iBoot family binaries. Similar public projects map the
entire binary as a big RWX blob, which negatively affects disassembler analysis.

> [!WARNING]
> Ibis should be treated as pre-release software. It has been tested against a
> wide array of binaries, but may have subtle errors. Please file an issue if
> you spot something wrong!

## Features & Roadmap

While Ibis' primary goal is to map segments correctly, some of the current and
planned features are detailed as follows:

- [x] Automatic detection and mapping of `TEXT`, `CONST`, `DATA`, and `BSS`
  segments with correct boundaries and permissions.
- [x] Function prologue detection (helps prevent run-on functions when
  disassemblers fail to identify `noreturn` functions).
- [ ] Automatic known function identification via string reference heuristics.
  (https://github.com/jonpalmisc/ibis/issues/2)
- [ ] Automatic detection & marking of outlined functions.
  (https://github.com/jonpalmisc/ibis/issues/4)
- [ ] 🔥🌸⁉️

See the [issues tab](https://github.com/jonpalmisc/ibis/issues) for a full list
of planned features or known issues.

## Installing

The Ibis plugins for Binary Ninja and IDA Pro are included in this repo and can
be installed with the included Makefile:

```sh
$ make install-binja
$ make install-ida
```

> [!IMPORTANT]
> The plugins expect that they have been installed via symlinks! This is done to
> avoid having to install Ibis' Python package globally or configure your
> disassembler to use a virtual environment. If you wish to install the plugins
> manually, replicate what is done in the Makefile.

## Troubleshooting

If a binary fails to load or the detected segments don't look quite right,
please file an issue! Ibis aims to provide widespread and accurate support for
iBoot-like binaries, so any analysis failures are considered a bug.

## Contributing

Any contributions that improve Ibis' analysis or support range are welcome! :)

### Testing

The included integration tests reference a "corpus" and "gauntlet", which are
collections of binaries I've used whilst developing this plugin. For a variety
of reasons (repo size, copyright issues, etc.) these are not included in the
repo. If you wish to contribute and run these tests, contact me and I can send
you the exact set I am using.

If you wish to assemble your own collection, `util/download.py` can be used to
download iBoot images in bulk, and [securerom.fun](https://securerom.fun/) has a
public collection of SecureROM dumps.

## License

Copyright © 2025 Jon Palmisciano. All rights reserved.

Licensed under the BSD 3-Clause license; the full terms of the license can be
found in [LICENSE.txt](LICENSE.txt).
