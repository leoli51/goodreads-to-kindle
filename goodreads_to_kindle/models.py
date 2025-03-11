from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class GoodReadsBook:
    authors: list[str]
    isbn: str
    isbn13: str
    language: str
    title: str

    @classmethod
    def from_scraped_item(cls, item: dict) -> GoodReadsBook:
        return cls(
            authors=item["author"],
            isbn=item["isbn"],
            isbn13=item["isbn13"],
            language=item["language"],
            title=item["title"],
        )
    

@dataclass(frozen=True)
class User:
    goodreads_id: str
    kindle_email: str
    supported_formats: list[str]
    books_sent_to_kindle: list[GoodReadsBook]

