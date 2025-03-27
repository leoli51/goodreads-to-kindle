import subprocess
from pathlib import Path
from exceptions import EbookConversionError


def convert_ebook(original_path: Path, format: str) -> str:
    new_path = original_path.with_suffix(".{format}")
    outcome = subprocess.run(["ebook-convert", original_path, new_path])
    if outcome != 0:
        raise EbookConversionError
    return new_path