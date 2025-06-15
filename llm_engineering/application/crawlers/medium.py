# libraries
from bs4 import BeautifulSoup
from loguru import logger

# modules
from llm_engineering.domain.documents import ArticleDocument
from .base import BaseSeleniumCrawler

class MediumCrawler(BaseSeleniumCrawler):
    model = ArticleDocument

    # 셀레늄에서 사용하는 기본 드라이버 옵션 확장
    def set_extra_driver_options(self, options) -> None:
        options.add_argument(r"--profile-directory=Profile 2")
    
    def extract(self, link: str, **kwargs) -> None:
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"해당 아티클은 이미 데이터베이스에 존재합니다. : {link}")
            return

        logger.info(f"미디움 아티클 스크래핑을 시작합니다. : {link}")

        # 셀레늄을 사용하여 페이지 로드
        self.driver.get(link)
        self.scroll_page()

        # BeautifulSoup을 사용하여 HTML 파싱
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # 메타데이터 추출
        title = soup.find_all("h1", class_="pw-post-title")
        subtitle = soup.find_all("h2", class_="pw-subtitle-paragraph")

        data = {
            "Title": title[0].string if title else None,
            "Subtitle": subtitle[0].string if subtitle else None,
            "Content": soup.get_text(),
        }

        self.driver.close()

        # 모델 인스턴스 생성
        user = kwargs["user"]
        instance = self.model(
            platform="medium",
            content=data,
            link=link,
            author_id=user.id,
            author_full_name=user.full_name,
        )
        instance.save()

        logger.info(f"아티클 스크래핑이 완료되었습니다. : {link}")