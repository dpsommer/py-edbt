.PHONY: init install trunk test coverage ci publish

TRUNK_INSTALLED=$(shell command -v trunk >/dev/null 2>&1 && echo 1 || echo 0)

init: install trunk test

install:
	@pip install -r requirements.txt
ifeq ($(TRUNK_INSTALLED), 0)
	@curl https://get.trunk.io -fsSL | bash -s -- -y
endif

trunk:
	@trunk fmt --all
	@trunk check

test:
	@pip install -qq --upgrade tox
	@tox -p

coverage:
	@pytest --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=src/edbt tests

ci:
	@pytest tests --junitxml=report.xml --assert=plain

publish:
	@pip install --upgrade twine
	@python -m build .
	twine upload dist/*
	@rm -rf build dist edbt.egg-info
