from abc import abstractmethod, ABC
from models import GoodReadsBook
from pathlib import Path

class BookProvider(ABC):

    @abstractmethod
    def download_book(self, book: GoodReadsBook, destination: Path) -> Path:
        ...

class ZlibBookProvider(BookProvider):

    def download_book(self, book: GoodReadsBook, destination: Path) -> Path:
       raise NotImplementedError
    
class AABookProvider(BookProvider):

    def download_book(self, book: GoodReadsBook, destination: Path) -> Path:
        raise NotImplementedError