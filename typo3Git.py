import scrapy

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class TYPO3GitSpider(scrapy.Spider):
    name = 'typo3gitspider'
    branch_url = 'https://github.com/TYPO3/TYPO3.CMS/branch_commits/'
    page_url = 'https://github.com/TYPO3/TYPO3.CMS/commits/master?page='
    start_urls = [
        'https://github.com/TYPO3/TYPO3.CMS/commits/master',
        # For debugging purposes
        # 'https://github.com/TYPO3/TYPO3.CMS/commits/master?page=50',
        # 'https://github.com/TYPO3/TYPO3.CMS/commits/master?page=601',
        # 'https://github.com/TYPO3/TYPO3.CMS/commit/8bd0c184357b2f211f8afba3eecc9a87e72e46d8',
    ]

    def parse(self, response):
        """
        Parse the commit list e.g.
        https://github.com/TYPO3/TYPO3.CMS/commits/master?page=1 to get the
        next page and all commits

        IDEA:
        Only parse first page, fetch amount of commits, devide by commits per
        page Create requests from back to front?  Check for existing json and
        count items, substract from amount of commits?  Navigate pagination to
        next commit list

        This way we can have incremental (much faster) parsing.
        """

        # Parse next page
        yield scrapy.Request(
                response.urljoin(self.get_next_page_url(response)),
                callback=self.parse,
                errback=self.errback,
                priority=10
            )

        # Parse commits
        for href in response.css('.commit-group a.sha::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(
                    full_url,
                    callback=self.parse_commit_details,
                    errback=self.errback,
                    priority=50
                )

    def parse_commit_details(self, response):
        """
        Parse the information of a single commit, e.g.
        https://github.com/TYPO3/TYPO3.CMS/commit/86bd2aedb790a600d03f1b3b6e287f058f5cb6d4
        """

        title = response.css('.commit-title ::text').extract_first().strip()
        sha = response.css('.sha-block .sha.user-select-contain::text')
        commit = {
            'type': self.get_commit_type(title),
            'title': title[title.rfind(']')+2:],
            'hash': sha.extract_first(),
        }

        response.meta['commit'] = commit

        #  Fetch branch information (version) via XHR
        yield scrapy.Request(
            self.branch_url + commit['hash'],
            callback=self.parse_commit_branch,
            errback=self.errback,
            priority=100,
            meta={'commit': commit}
        )

    def parse_commit_branch(self, response):
        """
        Parse branch information for a single commit, e.g.
        https://github.com/TYPO3/TYPO3.CMS/branch_commits/3c071aeff92965696808d33edb355a6a41d0f8af
        to determine the version this commit belongs to.
        """

        commit = response.meta['commit']
        branches = response.css('.branches-tag-list a::text').extract()

        try:
            branches = [
                branch for branch in branches if branch.rfind('TYPO3_') != -1
            ]
            commit['version'] = branches[-1][6:]
        except (IndexError):
            # If no branch for a specifc version can be found, use "dev"
            commit['version'] = 'dev'

        return commit

    def get_commit_type(self, title):
        """
        Determine the type of the commit, e.g. BUGFIX

        TODO: return usable information like "!!! FEATURE" -> "Breaking
        Change"?  Check which exist
        """

        return title[1:title.rfind(']')].replace('][', ' '),

    def get_next_page_url(self, response):
        """
        Get next page by calculation, as github disables some pagination links,
        like 101 on page 100 and we are not able to fetch them from response
        this way.
        """

        next_page = 1

        if response.url.rfind('=') != -1:
            next_page = int(response.url[response.url.rfind('=') + 1:]) + 1

        return self.page_url + str(next_page)

    def errback(self, failure):
        """
        Provide logging if some errors occur regarding response.
        """

        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
