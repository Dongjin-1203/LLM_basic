# libraries
import re
from urllib.parse import urlparse
from loguru import logger

# modules
from .base import BaseCrawler
from .custom_article import CustomArticleCrawler
from .linkedin import LinkedInCrawler
from .medium import MediumCrawler
from .github import GithubCrawler

class CrawlerDispatcher:
    def __init__(self) -> "None":
        self._crawlers = {}
    
    def build(cls) -> "CrawlerDispatcher":
        dispatcher = cls()

        return dispatcher
    
    # Medium 크롤러 등록
    def register_medium(self) -> "CrawlerDispatcher":
        self.medium = MediumCrawler()
        return self
    # LinkedIn 크롤러 등록
    def register_linkedin(self) -> "CrawlerDispatcher":
        self.linkedin = LinkedInCrawler()
        return self
    # GitHub 크롤러 등록
    def register_github(self) -> "CrawlerDispatcher":
        self.github = GithubCrawler()
        return self
    
    def register(self, domain: str, crawler: type[BaseCrawler]) -> "None":
        parser_domain = urlparse(domain)
        domain = parser_domain.netloc

        self._crawlers[r"https://(wwww\.)?{}?*".format(re.escape(domain))] = crawler

    def get_crawler(self, url: str) -> BaseCrawler:
        for pattern, crawler in self._crawlers.items():
            if re.match(pattern, url):
                return crawler()
        else:
            logger.warning(f"No crawler found for {url}. Defaulting to CustomArticleCrawler. ")
            
            return CustomArticleCrawler()