tui:
	@ python -m shgpt

repl:
	@ python -m shgpt -l

build:
	hatch build

clean:
	rm -rf build dist shgpt.egg-info

.PHONY: tui repl build clean
