PY=/usr/bin/env python
PYTHONPATH=.
PYTHONIOENCODING=UTF-8
PGPID=5BC8BE08

all: test sdist

pypi: sdist
	twine upload dist/*

sdist:
	PYTHONPATH=$(PYTHONPATH) $(PY) setup.py sdist

test:
	PYTHONIOENCODING=$(PYTHONIOENCODING) PYTHONPATH=$(PYTHONPATH) $(PY) t/test.py 2>&1 | tee test.log

clean:
	rm -rf dist src tftpy-doc* MANIFEST

flakes:
	pyflakes bin/*.py tftpy/*.py
