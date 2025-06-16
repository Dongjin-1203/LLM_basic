# libraries
from abc import ABC
from typing import Optional
from pydantic import UUID4, Field

# modules
from .base import NoSQLBaseDocument
from .types import DataCategory

# 다른 문서들의 추상 기본 모델. 상속받는 문서들에게 표준화된 구조 제공
class Document(NoSQLBaseDocument, ABC):
    content: dict
    platform: str
    author_id: UUID4 = Field(alias="author_id")
    author_full_name: str = Field(alias="author_full_name")

class UserDocument(NoSQLBaseDocument):
    first_name: str
    last_name: str

    class Settings:
        name = "users"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
class RepositoryDocument(Document):
    name: str
    link: str

    class Settings:
        name = DataCategory.REPOSITORIES
    
class ArticleDocument(Document):
    link: str
    
    class Settings:
        name = DataCategory.ARTICLES

class PostDocument(Document):
    image: Optional[str] = None
    link: str | None = None

    class Settings:
        name = DataCategory.POSTS