from goodreads_to_kindle.goodreads_scraper.crawl import crawl
import json
import time

from constants import LANG_MAP, DATA_FOLDER
from mail import EmailManager
from repository import JsonRepository
from settings import Settings
from models import GoodReadsBook
from exceptions import BookNotFoundException, EbookConversionError
from utils import convert_ebook
from book_provider import ZlibBookProvider

def main():
    settings = Settings()

    email_manager = EmailManager(
        smtp=settings.email_smtp,
        port=settings.email_smtp_port,
        user=settings.email_user,
        password=settings.email_password,
    )

    repository = JsonRepository(workdir=DATA_FOLDER)
    book_provider =  ZlibBookProvider()

    while True:
        for user in repository.list_users():
            print(f"Checking user {user.goodreads_id}")
            to_read_shelf = [GoodReadsBook.from_scraped_item(item) for item in crawl(user.goodreads_id, "to-read")]
            missing = [book for book in to_read_shelf if book not in user.books_sent_to_kindle]

            print(f"Found {len(missing)} new books")
            books_sent = []
            for book in missing:
                print(f"Finding book {book.title}")
                book_file_to_send = None

                # Search for the book in the repository
                book_paths = repository.get_book_paths(book.isbn)
                if book_paths:
                    # Check if we have a compatible extension
                    extensions = [path.suffix for path in book_paths]
                    for format in user.supported_formats:
                        if format in extensions:
                            book_file_to_send = repository.get_book_path(book.isbn, format)
                            print(f"Found book {book.title} in repository")
                            break
                    # If we don't have a compatible extension, try to convert
                    if not book_file_to_send:
                        try:
                            book_file_to_send = convert_ebook(book_paths[0], user.supported_formats[0])
                            print(f"Converted book {book.title} to {user.supported_formats[0]}")
                        except EbookConversionError:
                            print(f"Error converting book {book.title}")
                            continue
                
                # If we don't have the book, try to download it
                if not book_file_to_send:
                    try:
                        downloaded_book_file = book_provider.download_book(book, DATA_FOLDER)
                        book_file_to_send = repository.add_book_file(downloaded_book_file, book.isbn, book_file_to_send.suffix)
                        downloaded_book_file.unlink()
                        print(f"Book {book.title} downloaded.")
                    except BookNotFoundException:
                        print(f"Book {book.title} not found")
                        continue

                # Send the book
                email_manager.send_mail(
                    send_from=settings.email_from,
                    send_to=[user.kindle_email],
                    subject=f"GoodreadsToKindle - {book.title}",
                    text=f"This is your requested book: {book.title} by {book.author}.\n\n--\n\n",
                    files=[str(book_file_to_send)],
                )
                books_sent.append(book)
            
            # Update the user in the repository
            user.books_sent_to_kindle.extend(books_sent)
            repository.update_user(user)
        time.sleep(100)


if __name__ == "__main__":
    main()
