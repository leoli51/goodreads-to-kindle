from abc import ABC, abstractmethod
from models import User, GoodReadsBook
from os import path
from pathlib import Path
import shutil
import json
import glob

class Repository(ABC):

    @abstractmethod
    def list_users(self) -> list[User]:
        ...

    @abstractmethod
    def update_user(self, user: User) -> None:
        ...

    @abstractmethod
    def get_book_path(self, isbn: str, format: str) -> Path | None:
        ...

    @abstractmethod
    def get_book_paths(self, isbn: str) -> list[Path]:
        ...

    @abstractmethod
    def add_book_file(self, book_file_path: str, isbn: str, format: str) -> None:
        ...


class JsonRepository(Repository):

    BOOKS_PATH = "books"
    USERS_PATH = "users"

    def __init__(self, workdir: Path):
        self.workdir = workdir
        self.user_dir = workdir / self.USERS_PATH
        self.book_dir = workdir / self.BOOKS_PATH

    def list_users(self) -> list[User]:
        users = []
        for user_file in glob.glob(path.join(self.user_dir, "*.json")):
            with open(self.file_path, "r") as file:
                users.append(User(**user) for user in json.load(file))
        return users
    
    def update_user(self, user: User) -> None:
        with open(self.user_dir / f"{user.goodreads_id}.json", "w") as file:
            json.dump(user, file)

    def get_book_path(self, isbn: str, format: str) -> Path | None:
        book_file = self.book_dir / f"{isbn}.{format}"
        return book_file if book_file.exists() else None
    
    def get_book_paths(self, isbn: str):
        return [book_file for book_file in self.book_dir.glob(f"{isbn}.*")]

    def add_book_file(self, book_file_path: Path, isbn: str, format: str):
        return shutil.copy2(book_file_path, self.book_dir / f"{isbn}.{format}")