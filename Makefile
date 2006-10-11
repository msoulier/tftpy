PY=/usr/bin/env python
PYTHONPATH=lib

all: test sdist

sdist:
	PYTHONPATH=$(PYTHONPATH) $(PY) setup.py sdist

test:
	PYTHONPATH=$(PYTHONPATH) $(PY) t/test.py

clean:
	rm -rf dist src
