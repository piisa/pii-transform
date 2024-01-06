#  Manage package tasks
#  -----------------------------------
#  make pkg       -> build the package
#  make unit      -> perform unit tests
#  make install   -> install the package in a virtualenv
#  make uninstall -> uninstall the package from the virtualenv


# Package name
NAME := pii-transform

# Virtualenv to install in. In this order:
#   1. the one given by the VENV environment variable
#   2. an active one (as given by the VIRTUAL_ENV environment variable)
#   3. a default
VENV ?= $(shell echo $${VIRTUAL_ENV:-/opt/venv/pii})

PYTHON ?= python3.8
VENV_PYTHON ?= $(VENV)/bin/python3

# --------------------------------------------------------------------------

# Package version: taken from the __init__.py file
VERSION_FILE := src/pii_transform/__init__.py
VERSION	     := $(shell grep "^VERSION" $(VERSION_FILE) | sed -r "s/VERSION = \"(.*)\"/\1/")

PKGFILE := dist/$(NAME)-$(VERSION).tar.gz

# --------------------------------------------------------------------------

all:
	@echo "VERSION = $(VERSION)"
	@echo "use 'make pkg' to build the package"

build pkg: $(PKGFILE)

clean:
	rm -f "$(PKGFILE)"

rebuild: clean build

version:
	@echo "$(VERSION)"

backup: version
	tar cvjf $(NAME)-$(VERSION).tgz \
	  --exclude=__pycache__ --exclude=pii_transform.egg-info \
	  doc src test \
	  CHANGES.txt LICENSE README.md \
	  Makefile MANIFEST.in requirements.txt setup.py
	@echo "** Created $(NAME)-$(VERSION).tgz"

# --------------------------------------------------------------------------

TEST ?= test/unit

venv: $(VENV)

pytest: $(VENV)/bin/pytest

unit: venv pytest
	PYTHONPATH=src:test $(VENV)/bin/pytest $(ARGS) $(TEST)

unit-verbose: venv pytest
	PYTHONPATH=src:test \
		$(VENV)/bin/pytest -vv --capture=no $(ARGS) $(TEST)

unit-full: venv pytest
	PYTHONPATH=src:test:../pii-data/src:../pii-extract-base/src \
		$(VENV)/bin/pytest -vv --capture=no $(ARGS) $(TEST)

# --------------------------------------------------------------------------


$(PKGFILE): $(VERSION_FILE) setup.py
	$(VENV_PYTHON) setup.py sdist

$(VENV):
	BASE=$$(basename "$@"); test -d "$$BASE" || mkdir -p "$$BASE"
	$(PYTHON) -m venv $@
	$@/bin/pip install --upgrade pip
	$@/bin/pip install wheel

$(VENV)/bin/pytest: $(VENV)
	$(VENV)/bin/pip install pytest

install-dependencies: $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

install: $(PKGFILE) $(VENV)
	$(VENV)/bin/pip install $(PKGFILE)

uninstall: $(VENV)
	$(VENV)/bin/pip uninstall -y $(NAME)

reinstall: uninstall clean pkg install

install-local: $(VENV)
	$(VENV)/bin/pip install -e .

# -----------------------------------------------------------------------


TWINE := $(VENV)/bin/twine

$(TWINE):
	$(VENV)/bin/pip install twine

upload-check: $(PKGFILE) $(TWINE)
	$(TWINE) check $(PKGFILE)

upload-test: $(PKGFILE) $(TWINE)
	$(TWINE) upload --repository pypitest $(PKGFILE)

upload: $(PKGFILE) $(TWINE)
	$(TWINE) upload $(PKGFILE)
