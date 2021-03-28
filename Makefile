PIPENV = pipenv
all: ui docs

ui:
	$(MAKE) -C Gui/ _ui

clean:
	$(MAKE) -C Gui/ clean
	$(MAKE) -C doc/ clean

docs: sphinx latex
	
sphinx:
	$(PIPENV) run $(MAKE) -C doc/ sphinx

latex:
	$(MAKE) -C doc/ latex
