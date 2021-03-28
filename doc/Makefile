all: sphinx latex
sphinx:
	$(MAKE) -C sphinx_src/ html

latex:
	$(MAKE) -C LaTeX_src/ pdf
clean:
	$(MAKE) -C sphinx_src/ clean
	$(MAKE) -C LaTeX_src/ clean
