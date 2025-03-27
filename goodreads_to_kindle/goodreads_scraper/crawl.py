import json
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from .spiders.mybooks_spider import MyBooksSpider

def crawl(user_id: str, shelf: str, log_file: str = "scrapy.log") -> list[dict]:
    assert shelf in ["read", "to-read", "currently-reading", "all"], (
        "Shelf must be one of 'read', 'to-read', 'currently-reading', 'all'"
    )

    print(f"[crawl] Crawling Goodreads profile {user_id} for shelf '{shelf}'")

    settings = get_project_settings()
    settings.set("OUTPUT_FILE_SUFFIX", f"{user_id}")
    settings.set("LOG_FILE", log_file)
    settings.set("LOG_ENABLED", True)
    settings.set("FEEDS", {
        f"book_{user_id}.jl": {
            "format": "jsonlines",
            "overwrite": True,
        }
    })

    process = CrawlerProcess(settings)

    def on_item_scraped(item, response, spider):
        print(f"[item] Scraped: {item.get('title')} by {item.get('author')}")

    process.crawl(
        MyBooksSpider,
        user_id=user_id,
        shelf=shelf,
        item_scraped_callback=on_item_scraped,
    )

    process.start()  # <== blocks until done

    # Read output
    output_file = Path(f"book_{user_id}.jl")
    results = []
    if output_file.exists():
        with open(output_file) as f:
            for line in f:
                results.append(json.loads(line))
        output_file.unlink()

    #print(f"[crawl] Scraped {len(results)} books.")
    return results

import asyncio

async def fetch_want_to_read(user_id: str):
    return await asyncio.to_thread(crawl, user_id, "to-read")
