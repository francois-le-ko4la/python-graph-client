# Makefile

PACKAGE_NAME = "graphqlclient"
PACKAGE_DIR = $(PACKAGE_NAME)
MAKE := $(MAKE) --no-print-directory
SHELL = bash

default:
	@echo "Makefile for $(PACKAGE_NAME)"
	@echo
	@echo 'Usage:'
	@echo
	@echo '    user : make install                   install the packages'
	@echo '           make uninstall                 remove the package'
	@echo '    dev  : make venv                      install venv'
	@echo '           source venv/bin/activate       activate venv'
	@echo '           make dev                       install as dev'
	@echo '           make test                      test'
	@echo

venv:
	@pip3 install virtualenv --user
	@virtualenv venv

dev:
	@pip3 install -e ".[dev]"

install:
	@pip3 install . --upgrade

uninstall:
	@pip3 uninstall -y $(PACKAGE_NAME)

test:
	@pytest --pyargs $(PACKAGE_NAME)

publish:
	@pytest --pyargs $(PACKAGE_NAME)
	@git add .
	@git commit
	@git push

.PHONY: default init dev install uninstall doc stubs test example publish
