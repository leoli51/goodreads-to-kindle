from abc import abstractmethod, ABC
from models import GoodReadsBook
from pathlib import Path
from zlibrary import AsyncZlib, Language, Extension 
import requests
from exceptions import BookNotFoundException
import logging

logger = logging.getLogger(__name__)

class BookProvider(ABC):

    @abstractmethod
    def download_book(self, book: GoodReadsBook, destination: Path) -> Path:
        ...

class ZlibBookProvider(BookProvider):

    def __init__(self, email: str, password: str):
        self.lib = AsyncZlib()
        self.email = email
        self.password = password
        logging.getLogger("zlibrary").addHandler(logging.StreamHandler())
        logging.getLogger("zlibrary").setLevel(logging.DEBUG)


    async def download_book(self, book: GoodReadsBook, destination: Path) -> Path:
        logger.info("Logging in to Z-Library...")
        await self.lib.login(self.email, self.password)
        logger.info(f"Searching for book: {book.title}...")
        paginator = await self.lib.search(
            q=book.title,
            lang=[Language[book.language.upper()]] if book.language else [],
            extensions=[Extension.EPUB],
            count=50,
        )
        # No pagination due to not clear api behavior and lazyness..., lets retrieve up to 50 items, if its not there its not there...
        download_url = None
        items = await paginator.next()
        logging.info(f"Found {len(items)} items")
        for item in items:
            if (book.isbn13 and item.get("isbn") == book.isbn13) or (set(item.get("authors")) == set(book.authors) and item.get("name", "").lower() == book.title.lower()):
                logging.info(f"Found book: {item.get('name')}!")
                zlib_book = await item.fetch()
                download_url = zlib_book["download_url"]
                break

        if not download_url:
            raise BookNotFoundException
        logging.info(f"Downloading book: {book.title}...")
        download = requests.get(download_url, cookies=self.lib.cookies)
        downloaded_book_file_path = Path(f"{destination}/{book.get_file_name()}.{item['extension'].lower()}")
        with open(downloaded_book_file_path, "wb") as file:
            file.write(download.content)
        return downloaded_book_file_path

    
    async def test(self):
        await self.lib.login(self.email, self.password)
        available = await self.lib.profile.get_limits()
        print(available)

    

class AABookProvider(BookProvider):

    def download_book(self, book: GoodReadsBook, destination: Path) -> Path:
        raise NotImplementedError
    
if __name__ == "__main__":
    from dotenv import load_dotenv
    from settings import Settings
    import asyncio
    load_dotenv()
    settings = Settings()
    provider = ZlibBookProvider(email=settings.zlib_email, password=settings.zlib_password)
    asyncio.run(provider.test())
    # book = GoodReadsBook(authors=["Author"], isbn="123", isbn13="123", language="en", title="Title")
    # provider.download_book(book, Path("data"))