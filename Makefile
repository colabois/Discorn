PIPENV = pipenv
all: ui

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
