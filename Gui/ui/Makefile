PYUIC = pipenv run pyside2-uic
UI = $(wildcard *.ui)

%.py : %.ui %.py.diff
	$(PYUIC) $< > $@
	patch $@ < $@.diff

%.py.diff :
	cp default_diff $@

ui : $(UI:.ui=.py)

clean:
	rm *.py