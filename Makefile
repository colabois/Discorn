PIPENV = pipenv
all: ui

ui :
	$(MAKE) -C Gui/ _ui

clean :
	$(MAKE) -C Gui/ clean
	$(MAKE) -C doc/ clean

docs :
	$(PIPENV) run $(MAKE) -C doc/ html
