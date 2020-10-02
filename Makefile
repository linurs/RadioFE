all: 
	help2man -N --no-discard-stderr ./RadioFE.py -o RadioFE.1
	python setup.py sdist
	doxygen
