TEX = $(wildcard *.tex)
PDFLATEX = pdflatex --shell-escape -synctex=1 -interaction=nonstopmode

%.pdf : %.tex
	$(PDFLATEX) $<
	$(PDFLATEX) $<
	$(PDFLATEX) $< # Run three times to render correctly.

pdf : $(TEX:.tex=.pdf)

clean:
	rm *.pdf *.log *.aux *.synctex.gz *.toc || true
