# Makefile for Sphinx documentation

BUILDDIR      = build

DEPLOY_PATH   = /var/www/daniel-siepmann.de/sub/tmp/htdocs/stats/t3/versions

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo " Generation: "
	@echo "     install     to make standalone HTML files"
	@echo "     clean       to make standalone HTML files"
	@echo "     html        to make standalone HTML files"
	@echo "     deploy      to deploy the generated HTML to production"

.PHONY: install
install:
	pip install --user --upgrade -r requirements.txt

.PHONY: clean
clean:
	rm -rf $(BUILDDIR)/*

.PHONY: html
html: clean
	scrapy runspider typo3Docs.py -o $(BUILDDIR)/typo3Docs.json
	cp index.html $(BUILDDIR)/index.html
	@echo
	@echo "Published to $(BUILDDIR)/index.html"

.PHONY: deploy
deploy: clean html
	rsync --delete -vaz $(BUILDDIR)/* $(DEPLOY_PATH)

.PHONY: production
production: clean
	scrapy runspider typo3Docs.py --loglevel WARNING -o $(BUILDDIR)/typo3Docs.json
	cp index.html $(BUILDDIR)/index.html
	rsync --delete -az $(BUILDDIR)/* $(DEPLOY_PATH)
