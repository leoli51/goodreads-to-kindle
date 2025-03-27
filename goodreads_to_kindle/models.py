from __future__ import annotations

from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class GoodReadsBook:
    authors: list[str]
    isbn: str | None
    isbn13: str | None
    language: str | None
    title: str

    def get_file_name(self) -> str:
        authors = ', '.join(sorted(map(lambda a: a.lower(), self.authors)))
        file_name_parts = [self.title.lower(), authors]
        if self.language:
            file_name_parts.append(self.language.lower())
        return "___".join(file_name_parts)

    @classmethod
    def from_scraped_item(cls, item: dict) -> GoodReadsBook:
        return cls(
            authors=item["author"],
            isbn=item.get("isbn"),
            isbn13=item.get("isbn13"),
            language=item.get("language"),
            title=item["title"],
        )
    

@dataclass_json
@dataclass
class User:
    goodreads_id: str
    kindle_email: str
    books_sent_to_kindle: list[GoodReadsBook]

