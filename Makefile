PY=/usr/bin/env python
PYTHONPATH=.

all: test sdist tftpy-doc.tar.gz

sdist:
	PYTHONPATH=$(PYTHONPATH) $(PY) setup.py sdist

test:
	PYTHONPATH=$(PYTHONPATH) $(PY) t/test.py

apidocs: tftpy-doc

tftpy-doc:
	PYTHONPATH=$(PYTHONPATH) epydoc --html -o tftpy-doc tftpy

tftpy-doc.tar.gz: tftpy-doc
	-mkdir dist
	tar -zcvf dist/tftpy-doc.tar.gz tftpy-doc

clean:
	rm -rf dist src tftpy-doc* MANIFEST
