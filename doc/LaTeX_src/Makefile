TEX = $(wildcard *.tex)
PDFLATEX = pdflatex --shell-escape -synctex=1 -interaction=nonstopmode

%.pdf : %.tex
	$(PDFLATEX) $<

pdf : $(TEX:.tex=.pdf)

clean:
	rm *.pdf *.log *.aux *.synctex.gz || true
