# Ibis

Ibis is a Python library with accompanying disassembler plugins for analying
iBoot-like firmware, e.g.  SecureROM, iBoot, AVPBooter.

The primary goal of Ibis is to provide accurate memory layout information for a
wide range of iBoot family binaries. Other public projects often map the entire
binary as a big RWX blob, which negatively affects disassembler analysis.

## Plugins

A plugin for Binary Ninja and IDA Pro is included. These can be installed via
the the included makefile with `make install-binja` and `install-ida`,
respectively.

## License

Copyright © 2025 Jon Palmisciano. All rights reserved.

Licensed under the BSD 3-Clause license; the full terms of the license can be
found in [LICENSE.txt](LICENSE.txt).
