run:
	@ python -m shgpt.main

build:
	hatch build

clean:
	rm -rf build dist shgpt.egg-info

.PHONY: run build clean
