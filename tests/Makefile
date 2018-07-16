PYTHONEXE=python -B
# DO NOT rename it to PYTHONPATH as it will lead to weird issues!
PYTHON_INCLUDEPATH=../:$(PYTHONPATH)
PYTESTARGS=
COVARGS=--cov=pylock --cov-report=term-missing
# Once there will be more tests we might enable parallelism
#PYTESTARGS=-n 4

PYTHONTESTS=python/

all: test

test: unit

unit: python


python:
	PYTHONPATH=$(PYTHON_INCLUDEPATH) $(PYTHONEXE) -mpytest  ${COVARGS} $(PYTESTARGS) $(PYTHONTESTS) 

.PHONY: all unit python
