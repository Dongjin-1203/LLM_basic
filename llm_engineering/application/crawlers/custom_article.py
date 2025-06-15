# libraries
from urllib.parse import urlparse
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers.html2text import Html2TextTransformer
from loguru import logger

# modules
from llm_engineering.domain.documents import ArticleDocument
from .base import BaseCrawler
class CustomArticleCrawler(BaseCrawler):
    model = ArticleDocument
    # 중복 컨텐츠 제거를 위한 커스텀 크롤러 메서드
    def extract(self, link: str, **kwargs) -> None:
        """Extracts article content from a given link."""
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"해당 아티클은 이미 데이터베이스에 존재합니다. : {link}")
            return

        logger.info(f"아티클 스크래핑을 시작합니다. : {link}")

        loader = AsyncHtmlLoader(link)
        docs = loader.load()

        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        doc_transformed = docs_transformed[0]

        # 메타데이터 추출
        content = {
            "Title": doc_transformed.metadata.get("title"),
            "Subtitle": doc_transformed.metadata.get("description"),
            "Content": doc_transformed.page_content,
            "language": doc_transformed.metadata.get("language"),
        }

        # URL 파싱
        parsed_url = urlparse(link)
        platform = parsed_url.netloc

        # 모델 인스턴스 생성
        user = kwargs["user"]
        instance = self.model(
            content=content,
            link=link,
            platform=platform,
            author_id=user.id,
            author_full_name=user.full_name,
        )
        instance.save()

        logger.info(f"아티클 스크래핑이 완료되었습니다. : {link}")