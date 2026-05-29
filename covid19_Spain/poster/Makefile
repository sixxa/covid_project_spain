PDF=poster.pdf
TEX=poster.tex
DELIVERABLE=../covid19_Spain_poster.pdf

# Build with tectonic if available (self-contained, auto-fetches tikzposter);
# otherwise fall back to a TeX Live pdflatex install.
all: $(PDF)

$(PDF): $(TEX)
	@if command -v tectonic >/dev/null 2>&1; then \
		tectonic $(TEX); \
	else \
		pdflatex -interaction=nonstopmode -halt-on-error $(TEX); \
		pdflatex -interaction=nonstopmode -halt-on-error $(TEX); \
	fi
	cp $(PDF) $(DELIVERABLE)

clean:
	rm -f *.aux *.log *.out *.nav *.snm *.toc
