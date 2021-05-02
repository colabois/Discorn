PYUIC = pyside2-uic
UI = $(wildcard *.ui)

%.py : %.ui %.py.sh
	$(PYUIC) $< > $@
	bash $@.sh $@

%.py.sh :
	cp default_sh $@

ui : $(UI:.ui=.py)

clean:
	rm *.py || true
