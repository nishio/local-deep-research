from typing import Dict, List, Optional
import json
import os
from pathlib import Path
import asyncio
import aiofiles
from .deep_research import SearchResponse
from .book_metadata import BookMetadata

class LocalBookSearch:
    """Search through local book OCR data."""
    
    def __init__(self, base_dir: str = "from_pdf"):
        self.base_dir = Path(base_dir)
        
    async def search(
        self, query: str, limit: int = 5
    ) -> SearchResponse:
        """Search in book OCR data."""
        try:
            results = []
            book_dirs = self._find_book_directories()
            
            # 非同期で各書籍を検索
            tasks = []
            for book_dir in book_dirs:
                tasks.append(self._search_book(book_dir, query))
            
            # 全ての検索結果を収集
            all_results = await asyncio.gather(*tasks)
            for book_results in all_results:
                results.extend(book_results)
            
            # スコアでソートして上位の結果を返す
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            return {"data": results[:limit]}
            
        except Exception as e:
            print(f"Error searching books: {e}")
            return {"data": []}
    
    def _find_book_directories(self) -> List[Path]:
        """Find all book directories containing gyazo_info.json."""
        book_dirs = []
        for out_dir in self.base_dir.glob("out*"):
            for book_dir in out_dir.glob("*"):
                if book_dir.is_dir() and (book_dir / "gyazo_info.json").exists():
                    book_dirs.append(book_dir)
        return book_dirs
    
    async def _search_book(self, book_dir: Path, query: str) -> List[Dict[str, str]]:
        """Search within a single book."""
        try:
            metadata = BookMetadata.from_directory(book_dir)
            gyazo_file = book_dir / "gyazo_info.json"
            
            async with aiofiles.open(gyazo_file, mode='r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                results = []
                
                for item in data:
                    if "ocr_text" not in item:
                        continue
                        
                    text = item["ocr_text"]
                    score = self._calculate_score(query, text)
                    if score > 0:
                        excerpt = self._create_excerpt(text, query)
                        results.append({
                            "title": metadata.title,
                            "author": metadata.author,
                            "page": item.get("local_filename", ""),
                            "content": excerpt,
                            "score": score,
                            "isbn": metadata.isbn,
                            "url": item.get("permalink_url", "")
                        })
                
                return results
                
        except Exception as e:
            print(f"Error processing book {book_dir}: {e}")
            return []
    
    def _calculate_score(self, query: str, text: str) -> float:
        """Calculate similarity score between query and text."""
        query = query.lower()
        text = text.lower()
        
        # 完全一致の場合は高いスコア
        if query in text:
            return 1.0 + text.count(query) * 0.1  # 出現回数も考慮
            
        # 部分一致の場合は低いスコア
        words = query.split()
        matched_words = sum(1 for word in words if word in text)
        if matched_words > 0:
            return matched_words / len(words) * 0.5
            
        return 0.0
    
    def _create_excerpt(self, text: str, query: str, context_chars: int = 100) -> str:
        """Create excerpt with context around the matched query."""
        query_pos = text.lower().find(query.lower())
        if query_pos == -1:
            # クエリが見つからない場合は、部分一致で最も関連性の高い部分を探す
            words = query.lower().split()
            for word in words:
                word_pos = text.lower().find(word)
                if word_pos != -1:
                    query_pos = word_pos
                    break
            if query_pos == -1:
                return text[:200]  # 関連部分が見つからない場合は先頭から表示
            
        start = max(0, query_pos - context_chars)
        end = min(len(text), query_pos + len(query) + context_chars)
        
        excerpt = text[start:end]
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(text):
            excerpt = excerpt + "..."
            
        return excerpt
