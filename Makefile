.PHONY: init test coverage ci publish

init:
	pip install -r requirements.txt

test:
	pip install -qq --upgrade tox
	tox -p

coverage:
	pytest --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=src/edbt tests

ci:
	pytest tests --junitxml=report.xml --assert=plain

publish:
	pip install --upgrade twine
	python -m build .
	twine upload dist/*
	rm -rf build dist edbt.egg-info
