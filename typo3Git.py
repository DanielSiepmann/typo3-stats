#!/bin/env python

import scrapy


class TYPO3GitSpider(scrapy.Spider):
    name = 'typo3gitsionspider'
    branch_information = 'https://github.com/TYPO3/TYPO3.CMS/branch_commits/'
    start_urls = [
        'https://github.com/TYPO3/TYPO3.CMS/commits/master',
    ]

    # Parse a commit list of github
    def parse(self, response):
        # Navigate pagination to next commit list
        yield scrapy.Request(
                response.urljoin(
                    response.css('.pagination a::attr(href)')[-1].extract()
                ),
                callback=self.parse
            )

        # Parse commits
        for href in response.css('.commit-group a.sha::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_commit_details)

    # Parse a single commit detail view
    def parse_commit_details(self, response):
        title = response.css('.commit-title ::text').extract_first().strip()
        sha = response.css('.sha-block .sha.user-select-contain::text')
        commit = {
            'type': self.get_commit_type(title),
            'title': title[title.rfind(']')+2:],
            'hash': sha.extract_first(),
        }

        return [
                scrapy.Request(
                    self.branch_information + commit['hash'],
                    callback=self.parse_commit_branch,
                    meta={'commit': commit}
                )
        ]

    # Parse the commit of a branch (XHR)
    def parse_commit_branch(self, response):
        commit = response.meta['commit']
        branches = response.css('.branches-tag-list a::text').extract()

        try:
            commit['version'] = branches[-1][:3]
        except (IndexError):
            commit['version'] = 'dev'

        return [commit]

    def get_commit_type(self, title):
        # TODO: return usable information like "!!! FEATURE" -> "Breaking Change"?
        # Check which exist
        return title[1:title.rfind(']')].replace('][', ' '),
