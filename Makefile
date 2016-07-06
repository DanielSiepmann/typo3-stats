# Makefile for Sphinx documentation

BUILDDIR      = build
PUBLISHDIR    = public

DEPLOY_HOST   = daniel-siepmann.de
DEPLOY_PATH   = htdocs/daniel-siepmann.de
DEPLOY_PATH   = htdocs/tmp.daniel-siepmann.de/stats/t3/versions

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
	pip install --user --upgrade scrapy

.PHONY: clean
clean:
	rm -rf $(BUILDDIR)
	rm -rf $(PUBLISHDIR)
	mkdir $(BUILDDIR)
	mkdir $(PUBLISHDIR)

.PHONY: publish
publish:
	cp index.html $(PUBLISHDIR)/index.html
	@echo
	@echo "Published to $(PUBLISHDIR)/index.html"

.PHONY: docs
docs: clean
	scrapy runspider typo3Docs.py -o $(BUILDDIR)/typo3Docs.json --logfile $(BUILDDIR)/typo3Docs.log
	cp $(BUILDDIR)/typo3Docs.json $(PUBLISHDIR)/typo3Docs.json

.PHONY: github
github: clean
	scrapy runspider typo3Git.py -o $(BUILDDIR)/typo3Git.json --logfile $(BUILDDIR)/typo3Git.log
	cp $(BUILDDIR)/typo3Git.json $(PUBLISHDIR)/typo3Git.json

.PHONY: deploy
deploy: clean docs github publish
	rsync --delete -vaz $(PUBLISHDIR)/* $(DEPLOY_HOST):$(DEPLOY_PATH)
