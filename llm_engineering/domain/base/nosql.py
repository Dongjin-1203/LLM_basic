# libraries
import uuid
from abc import ABC
from typing import Generic, Type, TypeVar
from loguru import logger
from pydantic import UUID4, BaseModel, Field
from pymongo import errors

# modules
from llm_engineering.domain.exceptions import ImproperlyConfigured
from llm_engineering.infrastructure.db.mongo import connection
from llm_engineering.settings import settings

_database = connection.get_database(settings.DATABASE_NAME)

T = TypeVar("T", bound="NoSQLBaseDocument") # 파이썬 제네릭 모듈 활용 클래스의 타입을 일반화시킴

class NoSQLBaseDocument(BaseModel, ABC, Generic[T]):
    id: UUID4 = Field(default_factory=uuid.uuid4)

    # 고유 id 속성 기준으로 비교, 해시 가능한 컬렉션에 사용, 딕셔너리 키로 활용
    def __eq__(self, value: "object") -> bool:
        if not isinstance(value, self.__class__):
            return False
        return self.id == value.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    @classmethod
    # MongoDB에 저장된 데이터를 클래스 인스턴스로 변환하는 메서드
    def from_mongo(cls: Type[T], data: dict) -> T:
        if not data:
            raise ValueError("데이터가 비어있습니다.")
        id = data.pop("_id")
        return cls(**dict(data, id=id))
    
    def to_mongo(self: T, **kwargs) -> dict:
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", True)
        parsed = self.model_dump(
            exclude_unset=exclude_unset,
            by_alias=by_alias,
            **kwargs
        )

        if "_id" not in parsed and "_id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))

        for key, value in parsed.items():
            if isinstance(value, uuid.UUID):
                parsed[key] = str(value)
        return parsed
    
    # 모델 인스턴스를 MongGoDB에 저장하는 메서드
    def save(self: T, **kwargs) -> T | None:
        collection = _database[self.get_collection_name()]

        try:
            collection.instert_one(self.to_mongo(**kwargs))
            return self
        except errors.WriteError:
            logger.error("MongoDB에 저장할 수 없습니다.")
        return None
    
    @classmethod
    def get_collection_name(cls: Type[T]) -> str:
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise ImproperlyConfigured(f"Document should define a Settings cofiquration class with the name of the collection.")
        return cls.collection_name