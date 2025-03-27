from goodreads_scraper.crawl import fetch_want_to_read
from book_provider import ZlibBookProvider
from constants import LANG_MAP, DATA_FOLDER
from exceptions import BookNotFoundException
from mail import EmailManager
from models import GoodReadsBook
from repository import JsonRepository
from settings import Settings

import logging

def setup_logging(log_file: str = "main.log", level: int = logging.INFO):
    logger = logging.getLogger()  # root logger
    logger.setLevel(level)

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


async def main():
    settings = Settings()

    email_manager = EmailManager(
        smtp=settings.email_smtp,
        port=settings.email_smtp_port,
        user=settings.email_user,
        password=settings.email_password,
    )

    repository = JsonRepository(workdir=DATA_FOLDER)
    book_provider =  ZlibBookProvider(settings.zlib_email, settings.zlib_password)

    for user in repository.list_users():
        print(f"Checking user {user.goodreads_id}")
        to_read_shelf = [GoodReadsBook.from_scraped_item(item) for item in await fetch_want_to_read(user.goodreads_id)]
        missing = [book for book in to_read_shelf if book not in user.books_sent_to_kindle]

        print(f"Found {len(missing)} new books")
        for book in missing:
            print(f"Finding book {book.title}...")

            # Search for the book in the repository
            book_file_to_send = repository.get_book_path(book)

            # If we don't have the book, try to download it
            if not book_file_to_send:
                try:
                    downloaded_book_file = await book_provider.download_book(book, DATA_FOLDER)
                    book_file_to_send = repository.add_book_file(downloaded_book_file, book)
                    downloaded_book_file.unlink()
                    print(f"Book {book.title} downloaded.")
                except BookNotFoundException:
                    print(f"Book {book.title} not found")
                    continue
            else:
                print(f"Book {book.title} found in the repository")

            # Send the book
            if book_file_to_send:
                email_manager.send_mail(
                    send_to=[user.kindle_email],
                    subject=f"GoodreadsToKindle - {book.title}",
                    text=f"This is your requested book: {book.title} by {', '.join(book.authors)}.\n\n--\n\n",
                    file_paths=[str(book_file_to_send)],
                )
                print(f"Book {book.title} sent to {user.kindle_email}")

                # Update the user in the repository
                user.books_sent_to_kindle.append(book)
                repository.update_user(user)
        
        
    


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()
    setup_logging()

    asyncio.run(main())
