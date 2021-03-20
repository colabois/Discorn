all: ui

ui :
	$(MAKE) -C Gui/ _ui

clean :
	$(MAKE) -C Gui/ clean
	$(MAKE) -C doc/ clean

docs :
	$(MAKE) -C doc/ html
