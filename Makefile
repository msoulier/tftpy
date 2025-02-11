PY=/usr/bin/env python3
PYTHONPATH=.
PYTHONIOENCODING=UTF-8
PGPID=5BC8BE08
TESTCASE=

.PHONY: help all pypi sdist test clean flakes

help:
	@echo "Targets:"
	@echo "    all"
	@echo "    test"
	@echo "    sdist"
	@echo "    flakes"
	@echo "    clean"

all: test sdist

pypi: sdist
	twine upload dist/*

sdist:
	PYTHONPATH=$(PYTHONPATH) $(PY) setup.py sdist

test:
	rm -rf /tmp/foo
	PYTHONIOENCODING=$(PYTHONIOENCODING) PYTHONPATH=$(PYTHONPATH) $(PY) t/test.py $(TESTCASE) 2>&1 | tee test.log

clean:
	rm -rf dist src tftpy-doc* MANIFEST

flakes:
	pyflakes bin/*.py tftpy/*.py
