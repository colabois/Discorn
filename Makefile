PYUIC = pipenv run pyside2-uic
UI = $(wildcard *.ui)

%.py : %.ui
	$(PYUIC) $^ > $@

ui : $(UI:.ui=.py)