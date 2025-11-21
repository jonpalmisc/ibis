RM := rm -fr
LN := ln -s -f

BN_PLUGINS_PATH := ~/Library/Application\ Support/Binary\ Ninja/plugins
IDA_LOADERS_PATH := ~/.idapro/loaders

.PHONY: all
all:
	$(error Run 'make install-binja' or 'make install-ida' directly)

.PHONY: install-binja
install-binja:
	$(LN) $(shell pwd)/plugin/binja $(BN_PLUGINS_PATH)/view_ibis

.PHONY: install-ida
install-ida:
	$(LN) $(shell pwd)/plugin/ida/ibis.py $(IDA_LOADERS_PATH)/ibis.py

.PHONY: uninstall
uninstall:
	$(RM) $(IDA_LOADERS_PATH)/ibis.py
	$(RM) $(BN_PLUGINS_PATH)/view_ibis
