tui:
	python -m shellgpt -t $(args)

repl:
	python -m shellgpt -r $(args)

build: clean
	hatch build

clean:
	rm -rf build dist

fix:
	ruff check --fix
	ruff format

lint:
	ruff check
	ruff format --check

shell:
	hatch shell

ut:
	hatch run python -m unittest -v

contents:
	@ python download-contents.py

env:
	python3 -m venv env

dep:
	pip install -e .
	pip install -e "shellgpt.[tui]"

.PHONY: tui repl build clean fix lint shell contents dep
