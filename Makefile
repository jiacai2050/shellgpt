tui:
	@ python -m shellgpt -t

repl:
	@ python -m shellgpt -l

build: clean
	hatch build

clean:
	rm -rf build dist shellgpt.egg-info

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

.PHONY: tui repl build clean fix lint shell contents
