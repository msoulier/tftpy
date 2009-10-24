PY=/usr/bin/env python
PYTHONPATH=.

all: test sdist

sdist:
	PYTHONPATH=$(PYTHONPATH) $(PY) setup.py sdist

test:
	PYTHONPATH=$(PYTHONPATH) $(PY) t/test.py

doc: apidocs

apidocs: tftpy-doc

tftpy-doc:
	rm -rf html/tftpy-doc
	PYTHONPATH=$(PYTHONPATH) epydoc --html -o html/tftpy-doc tftpy

clean:
	rm -rf dist src tftpy-doc* MANIFEST
