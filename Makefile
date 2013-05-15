PY=/usr/bin/env python
PYTHONPATH=.

all: test sdist

sdist:
	PYTHONPATH=$(PYTHONPATH) $(PY) setup.py sdist

test:
	PYTHONPATH=$(PYTHONPATH) $(PY) t/test.py 2>&1 | tee test.log

clean:
	rm -rf dist src tftpy-doc* MANIFEST

flakes:
	pyflakes bin/*.py tftpy/*.py
