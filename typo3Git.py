#!/bin/env python

import scrapy


class TYPO3GitSpider(scrapy.Spider):
    name = 'typo3gitsionspider'
    start_urls = [
            'https://github.com/TYPO3/TYPO3.CMS/commits/master',
    ]

    def parse(self, response):
        for href in response.css('.pagination a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_commit_list)

    def parse_commit_list(self, response):
        for href in response.css('.commit-group a.sha::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_commit_details)

    def parse_commit_details(self, response):
        # Generate Ajax call for scraping?
        # Use commit hash for url and identification, just store what we need here and store association seperate?
        # branches = response.css('.branches-tag-list a::text').extract()
        # if (len(branches) == 0):
        #     print " !> No branches found for", response
        # else:
        #     print "!!!! Branches:", branches
        # yield {
        #     'version': response.css('.full-commit .branches-tag-list a:::text').extract()[:3],
        #     'changes': {
        #         'breaking': len(response.css('#breaking-changes a.reference.internal::text').extract()),
        #         'deprecation': len(response.css('#deprecation a.reference.internal::text').extract()),
        #         'feature': len(response.css('#features a.reference.internal::text').extract()),
        #         'important': len(response.css('#important a.reference.internal::text').extract()),
        #     }
        # }
