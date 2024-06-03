tui:
	@ python -m shgpt

repl:
	@ python -m shgpt -l

build: clean
	hatch build

clean:
	rm -rf build dist shgpt.egg-info

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

roles:
	@ python download-roles.py

.PHONY: tui repl build clean fix lint shell roles
