PIPENV = pipenv
all: discorn

discorn:
	$(MAKE) -C src/discorn all

clean: clean_doc clean_discorn
	
clean_discorn:
	$(MAKE) -C src/discorn clean

clean_doc:
	$(MAKE) -C doc/ clean

docs: sphinx latex
	
sphinx:
	$(PIPENV) run $(MAKE) -C doc/ sphinx

latex:
	$(MAKE) -C doc/ latex
