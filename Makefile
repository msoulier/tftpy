PY=/usr/bin/env python3
PYTHONPATH=.
PYTHONIOENCODING=UTF-8
PGPID=5BC8BE08
TESTCASE=

.PHONY: help all upload dist test clean flakes

help:
	@echo "Targets:"
	@echo "    all"
	@echo "    test - run all tests"
	@echo "    stdout - run stdout test"
	@echo "    stdin - run stdin test"
	@echo "    dist"
	@echo "    lint"
	@echo "    clean"

all: test dist

upload:
	twine upload --repository tftpy dist/*

dist:
	bin/git2cl > ChangeLog.md
	rm -rf dist
	mkdir dist
	python3 -m build

test: stdout stdin
	rm -rf /tmp/foo
	PYTHONIOENCODING=$(PYTHONIOENCODING) PYTHONPATH=$(PYTHONPATH) $(PY) tests/test.py $(TESTCASE) 2>&1 | tee test.log

stdout:
	PYTHONIOENCODING=$(PYTHONIOENCODING) PYTHONPATH=$(PYTHONPATH) $(PY) tests/stdout.py > /tmp/out

stdin:
	PYTHONIOENCODING=$(PYTHONIOENCODING) PYTHONPATH=$(PYTHONPATH) cat tests/640KBFILE | $(PY) tests/stdin.py

runserver:
	PYTHONPATH=$(PYTHONPATH) $(PY) bin/tftpy_server.py --ip=127.0.0.1 --port=6669 --root=/tmp
	# test 1 byte packet with "echo 'A' | nc -u 127.0.0.1 6669

clean:
	rm -rf dist src tftpy-doc* MANIFEST

lint:
	PYTHONPATH=$(PYTHONPATH) pylint --rcfile=.pylintrc bin/*.py tftpy/*.py 2>&1 | tee lint.log
