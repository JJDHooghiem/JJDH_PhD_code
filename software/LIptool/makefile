# Tools
LATEXMK = latexmk
RM = rm -f

# Filename
DOCNAME = *report
# Targets
all: doc
doc: pdf
pdf: $(DOCNAME).pdf

# Rules
%.pdf: %.tex
	$(LATEXMK) -silent -pdf -M -MP -MF $*.d $*

mostlyclean:
	$(LATEXMK) -silent -c 

clean: mostlyclean
	$(LATEXMK) -silent -C
	$(RM) *.run.xml *.synctex.gz
	$(RM) *.d

.PHONY: all clean doc mostlyclean pdf
