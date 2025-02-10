import pytest
from pathlib import Path
from ..book_metadata import BookMetadata

def test_book_metadata_extraction():
    """Test metadata extraction from directory name."""
    path = Path("メカニズムデザインで勝つ： ミクロ経済学のビジネス活用 坂井 豊貴 263p_4532358604")
    metadata = BookMetadata.from_directory(path)
    
    assert metadata.title == "メカニズムデザインで勝つ： ミクロ経済学のビジネス活用"
    assert metadata.author == "坂井 豊貴"
    assert metadata.pages == 263
    assert metadata.isbn == "4532358604"
    assert metadata.directory == path

def test_book_metadata_fallback():
    """Test fallback for invalid directory names."""
    path = Path("invalid_directory_name")
    metadata = BookMetadata.from_directory(path)
    
    assert metadata.title == "invalid_directory_name"
    assert metadata.author == ""
    assert metadata.pages == 0
    assert metadata.isbn == ""
    assert metadata.directory == path

def test_book_metadata_with_parentheses():
    """Test metadata extraction from directory name with parentheses."""
    path = Path("シン・ニホン AI×データ時代における日本の再生と人材育成 （NewsPicksパブリッシング） 安宅和人 444p_4910063048")
    metadata = BookMetadata.from_directory(path)
    
    assert metadata.title == "シン・ニホン AI×データ時代における日本の再生と人材育成 （NewsPicksパブリッシング）"
    assert metadata.author == "安宅和人"
    assert metadata.pages == 444
    assert metadata.isbn == "4910063048"
    assert metadata.directory == path
