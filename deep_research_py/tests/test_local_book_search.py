import pytest
from pathlib import Path
import json
import asyncio
from ..local_book_search import LocalBookSearch
from ..book_metadata import BookMetadata

@pytest.fixture
def test_book_dir(tmp_path):
    """Create a test book directory with sample OCR data."""
    book_dir = tmp_path / "out_test" / "テスト書籍 テスト著者 100p_1234567890"
    book_dir.mkdir(parents=True)
    
    # テスト用のJSONファイルを作成
    test_data = [{
        "ocr_text": "これはテストデータです。OCRで認識されたテキストの例です。",
        "local_filename": "test-001.jpg",
        "permalink_url": "https://example.com/test-001"
    }]
    
    with open(book_dir / "gyazo_info.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False)
    
    return book_dir

@pytest.mark.asyncio
async def test_local_book_search(test_book_dir):
    """Test book search functionality."""
    search = LocalBookSearch(str(test_book_dir.parent.parent))
    results = await search.search("テストデータ")
    
    assert len(results["data"]) > 0
    assert results["data"][0]["title"] == "テスト書籍"
    assert results["data"][0]["author"] == "テスト著者"
    assert "テストデータ" in results["data"][0]["content"]
    assert results["data"][0]["isbn"] == "1234567890"
    assert results["data"][0]["url"] == "https://example.com/test-001"
    assert results["data"][0]["score"] > 0

@pytest.mark.asyncio
async def test_local_book_search_no_match(test_book_dir):
    """Test search with no matching results."""
    search = LocalBookSearch(str(test_book_dir.parent.parent))
    results = await search.search("存在しないテキスト")
    
    assert len(results["data"]) == 0

@pytest.mark.asyncio
async def test_local_book_search_partial_match(test_book_dir):
    """Test search with partial word match."""
    search = LocalBookSearch(str(test_book_dir.parent.parent))
    results = await search.search("認識された")
    
    assert len(results["data"]) > 0
    assert results["data"][0]["score"] < 1.0  # 部分一致なので完全一致より低いスコア

def test_book_metadata_extraction():
    """Test metadata extraction from directory name."""
    path = Path("メカニズムデザインで勝つ： ミクロ経済学のビジネス活用 坂井 豊貴 263p_4532358604")
    metadata = BookMetadata.from_directory(path)
    
    assert metadata.title == "メカニズムデザインで勝つ： ミクロ経済学のビジネス活用"
    assert metadata.author == "坂井 豊貴"
    assert metadata.pages == 263
    assert metadata.isbn == "4532358604"
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

def test_book_metadata_fallback():
    """Test fallback for invalid directory names."""
    path = Path("invalid_directory_name")
    metadata = BookMetadata.from_directory(path)
    
    assert metadata.title == "invalid_directory_name"
    assert metadata.author == ""
    assert metadata.pages == 0
    assert metadata.isbn == ""
    assert metadata.directory == path
