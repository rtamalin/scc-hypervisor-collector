# define a PANDOC macro to hold command line for easier maintenance
define PANDOC
@pandoc $^ -f markdown-smart-raw_html -s -o $@
endef

# list of man pages to generate
PAGES=scc-hypervisor-collector.1 scc-hypervisor-collector.5 scc-hypervisor-collector.service.8

all: $(PAGES)

%.1: %.1.md
	$(PANDOC)

%.5: %.5.md
	$(PANDOC)

%.8: %.8.md
	$(PANDOC)

clean:
	rm $(PAGES)
