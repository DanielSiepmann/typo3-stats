#!/bin/env python

import scrapy


class TYPO3VersionSpider(scrapy.Spider):
    name = 'typo3versionspider'
    start_urls = [
        'https://docs.typo3.org/services/ajaxversions.php' +
        '?url=https://docs.typo3.org/typo3cms/extensions/core/',
    ]

    def parse(self, response):
        for version in response.css('a'):
            if version.css('::text').extract()[0].find('In one file:') == -1:
                full_url = response.urljoin(version.css('::attr(href)').extract()[0])
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_major_version
                )

    def parse_major_version(self, response):
        for href in response.css('nav [aria-label="main navigation"] .toctree-l1>a'):
            if href.css('::text').extract()[0].find('Documenting') == -1:
                full_url = response.urljoin(href.css('::attr(href)').extract()[0])
                yield scrapy.Request(full_url, callback=self.parse_version)

    def parse_version(self, response):
        yield {
            'version': response.css('h1::text').extract()[:3],
            'changes': {
                'breaking': len(response.css('#breaking-changes a.reference.internal::text').extract()),
                'deprecation': len(response.css('#deprecation a.reference.internal::text').extract()),
                'feature': len(response.css('#features a.reference.internal::text').extract()),
                'important': len(response.css('#important a.reference.internal::text').extract()),
            }
        }
