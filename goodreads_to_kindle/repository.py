from abc import ABC, abstractmethod
from models import User, GoodReadsBook
from os import path
from pathlib import Path
import shutil
import glob

class Repository(ABC):

    @abstractmethod
    def list_users(self) -> list[User]:
        ...

    @abstractmethod
    def update_user(self, user: User) -> None:
        ...

    @abstractmethod
    def get_book_path(self, book: GoodReadsBook) -> Path | None:
        ...

    @abstractmethod
    def add_book_file(self, book_file_path: str, book: GoodReadsBook) -> None:
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
            with open(user_file, "r") as file:
                users.append(User.from_json(file.read()))
        return users
    
    def update_user(self, user: User) -> None:
        with open(self.user_dir / f"{user.goodreads_id}.json", "w") as file:
            file.write(user.to_json())

    def get_book_path(self, book: GoodReadsBook) -> Path | None:
        book_file = self.book_dir / f"{book.get_file_name()}.epub"
        return book_file if book_file.exists() else None

    def add_book_file(self, book_file_path: Path, book: GoodReadsBook):
        return shutil.copy2(book_file_path, self.book_dir / f"{book.get_file_name()}.epub")


if __name__ == "__main__":
    from constants import DATA_FOLDER

    repository = JsonRepository(workdir=DATA_FOLDER)
    book = GoodReadsBook(authors=["Author"], isbn="123", isbn13="123", language="en", title="Title")
    users = repository.list_users()
    print(users)
    users[0].books_sent_to_kindle.append(book)
    repository.update_user(users[0])
    print(repository.list_users())