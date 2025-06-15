# libraries
from loguru import logger
import tempfile
import os
import subprocess
import shutil

# modules
from .base import BaseCrawler
from llm_engineering.domain.documents import RepositoryDocument

class GithubCrawler(BaseCrawler):
    model = RepositoryDocument

    # ignore: tuple[str, ...]  # 파일 확장자 무시 목록
    def __init__(self, ignore=(".git", ".toml", ".lock", ".png")):
        super().__init__()
        self.ignore = ignore

    # 갖고온 리포지토리가 DB에 있는지 확인하는 메서드
    def extract(self, link: str, **kwargs) -> None:
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"리포지토리가 이미 데이터베이스에 있습니다. : {link}")
            return
        # 리포지토리 스크랩 시작
        logger.info(f"Github 리포지토리 스크랩을 시작하겠습니다. : {link}")
        repo_name = link.rstrip("/").split("/")[-1]
        local_temp = tempfile.mkdtemp()

        # 현재 작업 디렉토리를 임시 디렉토리로 변경
        try:
            os.chdir(local_temp)
            subprocess.run(["git", "clone", link])
            # 클론에 성공한 후 클론된 리포지토리의 경로 생성
            repo_path = os.path.join(local_temp, os.listdir(local_temp)[0])

            tree = {}
            for root, _, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                if dir.startswith(self.ignore):
                    continue

                for file in files:
                    if file.endswith(self.ignore):
                        continue
                    file_path = os.path.join(dir, file)
                    with open(file_path, "r", errors="ignore") as f:
                        tree[file_path] = f.read().replace(" ", "") # 공백 제거

            # 새 인스턴스 생성, 세부정보 작성 및 MongoDB에 저장
            user = kwargs["user"]
            instance = self.model(
                content=tree, 
                name=repo_name, 
                link=link, 
                platform="github", 
                author_id = user.id, 
                author_full_name=user.full_name,
            )
            instance.save()
        # 스크래핑 성공 여부 예외 발생 여부 상관 없이 임시 디렉토리를 삭제
        except Exception:
            raise
        finally:
            shutil.rmtree(local_temp)
        logger.info(f"Github 리포지토리 스크랩이 완료되었습니다. : {link}")