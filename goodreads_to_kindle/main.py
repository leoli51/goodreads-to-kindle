from crawl import crawl
import json
import time

from email.message import EmailMessage
import os
import smtplib
from constants import LANG_MAP, DATA_FOLDER
from dotenv import load_dotenv
from query import get_book, download_book

load_dotenv(override=True)

EMAIL_SMTP = os.getenv("EMAIL_SMTP")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
KINDLE_EMAIL = os.getenv("KINDLE_EMAIL")
GOODREADS_ID = os.getenv("GOODREADS_ID")


def send_mail(send_from, send_to, subject, text, files):
    # assert isinstance(send_to, list)

    email = EmailMessage()
    email["From"] = send_from
    email["To"] = send_to
    email["Subject"] = subject
    email.set_content(text)
    # attach files
    for file in files:
        with open(file, "rb") as f:
            file_data = f.read()
            email.add_attachment(
                file_data,
                maintype="application",
                subtype="octet-stream",
                filename=os.path.basename(file),
            )
    server = smtplib.SMTP(EMAIL_SMTP, port=EMAIL_SMTP_PORT)
    server.starttls()
    server.login(send_from, EMAIL_PASSWD)
    server.sendmail(send_from, send_to, email.as_string())
    server.quit()


def main():
    while True:
        DATA_FOLDER.mkdir(exist_ok=True)
        user_file = DATA_FOLDER / f"{GOODREADS_ID}.jl"
        old_shelf = []
        if user_file.exists():
            with open(user_file) as f:
                for line in f:
                    book = json.loads(line)
                    old_shelf.append(book)
        result = crawl(GOODREADS_ID, "to-read")
        # update the user file
        with open(user_file, "w") as f:
            for book in result:
                f.write(json.dumps(book) + "\n")
        # get difference between result and old_shelf
        missing = [book for book in result if book not in old_shelf]
        print(f"Found {len(missing)} new books")
        for book in missing:
            title = book["title"]
            author = book["author"][0]
            isbn = book.get("isbn", None)
            lang = LANG_MAP[book["language"]]
            book_results = get_book(title, author, lang, isbn)
            if not book_results:
                print(f"Book {title} not found")
                continue
            book_path = download_book(book_results, DATA_FOLDER)
            if not book_path:
                print(f"Error downloading book {title}")
                continue
            print("Book downloaded. Sending to kindle email")
            send_mail(
                send_from=EMAIL_FROM,
                send_to=[KINDLE_EMAIL],
                subject="GoodreadsToKindle - " + str(title),
                text=f"This is your requested book: {title} by {author}.\n\n--\n\n",
                files=[str(book_path)],
            )
            print("Cleaning up...")
            book_path.unlink()
        time.sleep(5 * 1)


if __name__ == "__main__":
    main()
