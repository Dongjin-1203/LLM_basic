# libraies
from abc import ABC, abstractmethod
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from tempfile import mkdtemp

from llm_engineering.domain.documents import NoSQLBaseDocument

# chromedriver의 현재버전을 체크 / 없을경우 설치한 후 설치 경로 추가
chromedriver_autoinstaller.install()
class BaseCrawler(ABC):
    model: type[NoSQLBaseDocument]

    @abstractmethod
    # 링크 입력받는 메서드
    def extract(self, link: str, **kwargs) -> None: ...

class BaseSeleniumCrawler(BaseCrawler, ABC):
    # 헤드리스 모드 크롤링 표준설정
    def __init__(self, scroll_limit: int = 5) -> None:
        options = webdriver.ChromeOptions()

        # 크롬 설정
        options.add_argument("--no-sandbox")
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9226")

        # set_extra_driver_options활용 추가 드라이버 옵션 설정
        self.set_extra_driver_options(options)

        self.driver = webdriver.Chrome(options=options,)

    def set_extra_driver_options(self, options: Options) -> None:
        """Override this method to set additional driver options."""
        pass
    def login(self) -> None:
        """Override this method to implement login functionality."""
        pass
    # 스크롤 다운 메서드
    def scroll_down(self) -> None:
        current_scroll = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height or (self.scroll_limit and current_scroll >= self.scroll_limit):
                break

            last_height = new_height
            current_scroll += 1