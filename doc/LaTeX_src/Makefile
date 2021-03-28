TEX = $(wildcard *.tex)
PDFLATEX = pdflatex --shell-escape -synctex=1 -interaction=nonstopmode

%.pdf : %.tex
	$(PDFLATEX) $<
	$(PDFLATEX) $< # Run twice for the table of contents

pdf : $(TEX:.tex=.pdf)

clean:
	rm *.pdf *.log *.aux *.synctex.gz *.toc || true
