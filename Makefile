PY=/usr/bin/env python
PYTHONPATH=lib

all: test sdist epydoc

sdist:
	PYTHONPATH=$(PYTHONPATH) $(PY) setup.py sdist

test:
	PYTHONPATH=$(PYTHONPATH) $(PY) t/test.py

epydoc:
	PYTHONPATH=$(PYTHONPATH) epydoc --html -o epydoc tftpy

clean:
	rm -rf dist src epydoc MANIFEST
