import os
from typing import Optional

import chromadb

from app.config import get_settings

settings = get_settings()


class KnowledgeBaseService:
    """Service for managing the city knowledge base using ChromaDB."""

    _instance = None
    _client = None
    _collection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize ChromaDB client and collection."""
        persist_dir = settings.chroma_persist_dir

        # Ensure directory exists
        os.makedirs(persist_dir, exist_ok=True)

        self._client = chromadb.PersistentClient(path=persist_dir)

        # Get or create collection
        self._collection = self._client.get_or_create_collection(
            name="city_knowledge",
            metadata={"description": "Lüneburg city services knowledge base"},
        )

    def add_documents(self, documents: list[dict]):
        """
        Add documents to the knowledge base.

        Each document should have:
        - id: unique identifier
        - content: the text content
        - metadata: dict with category, filename, etc.
        """
        if not documents:
            return

        ids = [doc["id"] for doc in documents]
        contents = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        self._collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas,
        )

    def query(
        self,
        query: str,
        category: Optional[str] = None,
        n_results: int = 3,
    ) -> list[dict]:
        """
        Query the knowledge base for relevant information.

        Args:
            query: The search query
            category: Optional filter for specific category
            n_results: Number of results to return

        Returns:
            List of matching documents with content, metadata, and score
        """
        where_filter = None
        if category:
            where_filter = {"category": category}

        results = self._collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
        )

        # Format results
        formatted = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": 1 - (results["distances"][0][i] if results["distances"] else 0),
                })

        return formatted

    def delete_all(self):
        """Delete all documents from the collection."""
        all_docs = self._collection.get()
        if all_docs["ids"]:
            self._collection.delete(ids=all_docs["ids"])

    def get_status(self) -> dict:
        """Get the current status of the knowledge base."""
        count = self._collection.count()
        return {
            "document_count": count,
            "collection_name": "city_knowledge",
        }
