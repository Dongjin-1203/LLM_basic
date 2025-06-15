def BaseCrawler():
    """
    Base class for crawlers.
    This class should be inherited by all crawlers.
    It provides a common interface and some basic functionality.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the base crawler.
        """
        pass

    def crawl(self, *args, **kwargs):
        """
        Method to start crawling.
        Should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")