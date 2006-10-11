PY=/usr/bin/python

all: test sdist

sdist:
	$(PY) setup.py sdist

test:
	$(PY) t/test.py

clean:
	rm -rf dist
