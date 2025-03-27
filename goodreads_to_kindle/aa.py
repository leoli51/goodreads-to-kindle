import requests
from pathlib import Path

from typing import Optional
import logging
import os

HEADERS = {
    "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
    "x-rapidapi-host": os.getenv("RAPID_API_HOST"),
}
URL = f"https://{os.getenv('RAPID_API_HOST')}"


def get_book(
    title: str,
    author: str,
    language: str,
    isbn: Optional[str],
    preferred_format: str = "epub",
) -> Optional[list[dict]]:
    # first attempt to find the book in the preferred format,
    # using title and author
    print(f"Searching for {title} by {author}, {language=}")
    querystring = {
        "q": title.replace("'", " "),
        "authors": author,
        "skip": "0",
        "limit": "10",
        "sort": "mostRelevant",
        "lang": language,
    }
    response = requests.get(f"{URL}/search", headers=HEADERS, params=querystring)
    result = response.json()
    if result["total"] > 0:
        # sort list of books putting the preferred format first, keeping the order of the others
        books = response.json()["books"]
        books.sort(key=lambda x: x["format"] == preferred_format, reverse=True)
        return books
    else:
        logging.info(f"Book {title} not found")
        return None


def download_book(books: list[dict], output_folder: Path) -> Optional[Path]:
    for book in books:
        md5 = book["md5"]
        title = book["title"]
        format = book["format"]
        print(f"Downloading book {title}, {md5=}")
        querystring = {"md5": md5}
        response = requests.get(f"{URL}/download", headers=HEADERS, params=querystring)
        try:
            book_url = response.json()[0]
            book_file = requests.get(book_url, allow_redirects=True)
            with open(output_folder / f"{title}.{format}", "wb+") as f:
                f.write(book_file.content)
            print("Book downloaded")
            return output_folder / f"{title}.{format}"
        except requests.exceptions.RequestException as e:
            print("Error, retrying")
            print(e)
    return None
