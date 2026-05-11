"""
Roobie Vector Store
ChromaDB-backed vector memory for semantic search over code, research, and skills.
"""

from typing import List, Dict, Optional
from pathlib import Path


class VectorStore:
    """ChromaDB vector store for semantic search."""
    
    def __init__(self, persist_dir: str = "~/.roobie/chroma"):
        self.persist_dir = Path(persist_dir).expanduser()
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collections = {}
    
    @property
    def client(self):
        if self._client is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(path=str(self.persist_dir))
            except ImportError:
                raise ImportError("chromadb required: pip install chromadb")
        return self._client
    
    def get_collection(self, name: str):
        if name not in self._collections:
            self._collections[name] = self.client.get_or_create_collection(
                name=name, metadata={"hnsw:space": "cosine"})
        return self._collections[name]
    
    def add_documents(self, collection_name: str, documents: List[str],
                      ids: List[str], metadatas: List[Dict] = None):
        coll = self.get_collection(collection_name)
        coll.add(documents=documents, ids=ids, metadatas=metadatas or [{}]*len(documents))
    
    def search(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict]:
        coll = self.get_collection(collection_name)
        results = coll.query(query_texts=[query], n_results=n_results)
        output = []
        for i, doc in enumerate(results["documents"][0]):
            output.append({
                "document": doc,
                "id": results["ids"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0,
            })
        return output
    
    def delete_collection(self, name: str):
        self.client.delete_collection(name)
        self._collections.pop(name, None)
