PIPENV = pipenv
all: Corner


Corner:
	$(PIPENV) run $(MAKE) -C corner all


clean: clean_doc clean_corner


clean_corner:
	$(MAKE) -C corner clean


clean_doc:
	$(MAKE) -C doc/ clean


docs: sphinx latex


doc: sphinx latex


sphinx:
	$(PIPENV) run $(MAKE) -C doc/ sphinx


latex:
	$(MAKE) -C doc/ latex


.PHONY: docs doc all clean
