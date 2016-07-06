#!/bin/env python

import scrapy


class TYPO3GitSpider(scrapy.Spider):
    name = 'typo3gitsionspider'
    branch_information = 'https://github.com/TYPO3/TYPO3.CMS/branch_commits/'
    start_urls = [
        'https://github.com/TYPO3/TYPO3.CMS/commits/master',
    ]

    def parse(self, response):
        for href in response.css('.pagination a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_commit_list)

    def parse_commit_list(self, response):
        self.parse(response)

        for href in response.css('.commit-group a.sha::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_commit_details)

    def parse_commit_details(self, response):
        title = response.css('.commit-title ::text').extract_first().strip()

        commit = {
            'type': self.get_commit_type(title),
            'title': title[title.rfind(']')+2:],
            'hash': response.css('.sha-block .sha.user-select-contain::text').extract_first(),
        }

        return [scrapy.Request(self.branch_information + commit['hash'], callback=self.parse_commit_branch, meta={'commit': commit})]

    def parse_commit_branch(self, response):
        commit = response.meta['commit']

        # TODO: Fix issue:
        #    2016-07-06 17:53:23 [scrapy] ERROR: Spider error processing <GET https://github.com/TYPO3/TYPO3.CMS/branch_commits/2bc918df67213c8539a768647f279c8861aa5fa6> (
        #    referer: https://github.com/TYPO3/TYPO3.CMS/commit/2bc918df67213c8539a768647f279c8861aa5fa6)
        #    Traceback (most recent call last):
        #    File "/Users/siepmann/Library/Python/2.7/lib/python/site-packages/twisted/internet/defer.py", line 588, in _runCallbacks
        #        current.result = callback(current.result, *args, **kw)
        #    File "/Users/siepmann/Projects/own/t3-stats/typo3Git.py", line 38, in parse_commit_branch
        #        commit['version'] = response.css('.branches-tag-list a::text').extract()[-1][:3]
        #    IndexError: list index out of range
        commit['version'] = response.css('.branches-tag-list a::text').extract()[-1][:3]

        return [commit]

    def get_commit_type(self, title):
        # TODO: return usable information like "!!! FEATURE" -> "Breaking Change"?
        # Check which exist
        return title[1:title.rfind(']')].replace('][', ' '),
