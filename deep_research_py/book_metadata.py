from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class BookMetadata:
    """Book metadata extracted from directory name."""
    title: str
    author: str
    pages: int
    isbn: str
    directory: Path

    @classmethod
    def from_directory(cls, directory: Path) -> "BookMetadata":
        """Extract metadata from directory name.
        
        Example directory name:
        メカニズムデザインで勝つ： ミクロ経済学のビジネス活用 坂井 豊貴 263p_4532358604
        """
        pattern = r"(.+?)\s+([^\d]+?)\s+(\d+)p_(\d+)$"
        match = re.match(pattern, directory.name)
        if not match:
            # フォールバック：ディレクトリ名をそのままタイトルとして使用
            return cls(
                title=directory.name,
                author="",
                pages=0,
                isbn="",
                directory=directory
            )
        
        title, author, pages, isbn = match.groups()
        return cls(
            title=title.strip(),
            author=author.strip(),
            pages=int(pages),
            isbn=isbn,
            directory=directory
        )
