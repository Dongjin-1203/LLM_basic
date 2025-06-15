def CrawlerDispatcher(crawler_name: str, *args, **kwargs):
    """
    Dispatcher function to call the appropriate crawler based on the crawler_name.
    """
    from llm_engineering.application.crawlers import (
        arxiv_crawler,
        github_crawler,
        google_scholar_crawler,
        youtube_crawler,
    )

    crawlers = {
        "arxiv": arxiv_crawler.ArXivCrawler,
        "github": github_crawler.GitHubCrawler,
        "google_scholar": google_scholar_crawler.GoogleScholarCrawler,
        "youtube": youtube_crawler.YouTubeCrawler,
    }

    if crawler_name not in crawlers:
        raise ValueError(f"Crawler '{crawler_name}' is not supported.")

    return crawlers[crawler_name](*args, **kwargs)