tui:
	@ python -m shgpt

repl:
	@ python -m shgpt -l

build: clean
	hatch build

clean:
	rm -rf build dist shgpt.egg-info


lint:
	ruff check
	ruff format

shell:
	hatch shell

roles:
	@ python download-roles.py

.PHONY: tui repl build clean lint shell roles
