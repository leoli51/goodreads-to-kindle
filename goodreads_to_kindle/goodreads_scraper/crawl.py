from rich.progress import Progress, TaskID
from rich.progress import (
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
)
from scrapy.utils.reactor import install_reactor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from pathlib import Path
import json
import sys

from items import BookItem

def crawl(user_id: str, shelf: str, log_file: str = "scrapy.log") -> list[dict]:
    """
    Crawl a Goodreads profile for books on a specified shelf.

    Args:
        user_id (str): The Goodreads user ID to crawl.
        shelf (str): The shelf to crawl. Must be one of 'read', 'to-read', 'currently-reading', 'all'.
        log_file (str): The log file for scrapy logs.

    Returns:
        list[dict]: A list of dictionaries containing the scraped

    This function initializes a progress updater with an infinite spinner and starts a Scrapy
    crawler process to scrape books from the specified shelf of the given Goodreads user profile.
    The scraped data is processed and saved according to the project settings.
    """
    assert shelf in ["read", "to-read", "currently-reading", "all"], (
        "Shelf must be one of 'read', 'to-read', 'currently-reading', 'all'"
    )
    print(f"Crawling Goodreads profile {user_id} for shelf {shelf}")

    # On "My Books", each page of has about ~30 books
    # The last page may have less
    # However, we don't know how many total books there could be on a shelf
    # So until we can figure it out, show an infinite spinner
    progress_updater = ProgressUpdater(infinite=True)

    with progress_updater.progress:
        progress_updater.add_task_for(
            BookItem, description=f"[red]Scraping books for shelf '{shelf}'..."
        )
        settings = get_project_settings()
        # used by the JsonLineItem pipeline
        settings.set("OUTPUT_FILE_SUFFIX", f"{user_id}")
        # Emit all scrapy logs to log_file instead of stderr
        settings.set("LOG_FILE", log_file)
        install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")
        process = CrawlerProcess(settings)
        process.crawl(
            "mybooks",
            user_id=user_id,
            shelf=shelf,
            item_scraped_callback=progress_updater,
        )
        # CLI will block until this call completes
        process.start()
        del sys.modules["twisted.internet.reactor"]

    # read results from the output file
    output_file = Path(__file__).parent / f"book_{user_id}.jl"
    author_file = Path(__file__).parent / f"author_{user_id}.jl"
    output = []
    with open(output_file) as f:
        for line in f:
            output.append(json.loads(line))
    output_file.unlink()
    author_file.unlink()
    return output


class ProgressUpdater:
    """Callback class for updating the progress on the console.

    Internally, this maintains a map from the item type to a TaskID.
    When the callback is invoked, it tries to find a match for the scraped item,
    and advance the corresponding task progress.
    """

    def __init__(self, infinite=False):
        if infinite:
            self.progress = Progress(
                "[progress.description]{task.description}",
                TimeElapsedColumn(),
                TextColumn("{task.completed} items scraped"),
                SpinnerColumn(),
            )
        else:
            self.progress = Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
                "/",
                TimeElapsedColumn(),
            )
        self.item_type_to_task = {}

    def add_task_for(self, item_type, *args, **kwargs) -> TaskID:
        task = self.progress.add_task(*args, **kwargs)
        self.item_type_to_task[item_type] = task
        return task

    def __call__(self, item, spider):
        item_type = type(item)
        task = self.item_type_to_task.get(item_type, None)
        if task is not None:
            self.progress.advance(task)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    print(crawl("166551569-leonardo-la-rocca", "to-read"))
