import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional
import os
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings  # Can be changed to other embeddings
from langchain_core.documents import Document
import uuid

logger = logging.getLogger(__name__)

class QdrantVectorDB:
    """
    Qdrant Vector Database Service for RAG functionality
    """

    def __init__(self, host: str = None, port: int = None, collection_name: str = "ledger_data"):
        """
        Initialize Qdrant client

        Args:
            host: Qdrant host (defaults to environment variable QDRANT_HOST or localhost)
            port: Qdrant port (defaults to environment variable QDRANT_PORT or 6333)
            collection_name: Name of the collection to use for storing vectors
        """
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = port or int(os.getenv("QDRANT_PORT", 6333))
        self.collection_name = collection_name

        # Initialize the Qdrant client
        try:
            self.client = QdrantClient(host=self.host, port=self.port)
            logger.info(f"Connected to Qdrant at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise

    def create_collection(self, vector_size: int = 1536, distance_metric: str = "Cosine"):
        """
        Create a collection in Qdrant for storing document vectors

        Args:
            vector_size: Size of the embedding vectors (default 1536 for OpenAI embeddings)
            distance_metric: Distance metric for similarity search (Cosine, Euclid, Manhattan, Dot)
        """
        try:
            # Define distance metric mapping
            distance_map = {
                "Cosine": models.Distance.COSINE,
                "Euclid": models.Distance.EUCLID,
                "Manhattan": models.Distance.MANHATTAN,
                "Dot": models.Distance.DOT
            }

            distance = distance_map.get(distance_metric, models.Distance.COSINE)

            # Check if collection already exists
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]

            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return

            # Create the collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=distance),
            )

            logger.info(f"Created collection '{self.collection_name}' with vector size {vector_size}")
        except Exception as e:
            logger.error(f"Failed to create collection '{self.collection_name}': {e}")
            raise

    def add_documents(self, documents: List[Document], embeddings_model=None):
        """
        Add documents to the Qdrant collection

        Args:
            documents: List of LangChain Document objects
            embeddings_model: Embedding model to use for vectorization
        """
        if embeddings_model is None:
            # Use OpenAI embeddings by default, but can be configured differently
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for embeddings")
            embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")

        try:
            # Create Qdrant vector store
            qdrant_store = Qdrant.from_documents(
                documents=documents,
                embedding=embeddings_model,
                url=f"http://{self.host}:{self.port}",
                collection_name=self.collection_name,
                force_recreate=False
            )

            logger.info(f"Added {len(documents)} documents to collection '{self.collection_name}'")
            return qdrant_store
        except Exception as e:
            logger.error(f"Failed to add documents to collection '{self.collection_name}': {e}")
            raise

    def search(self, query: str, embeddings_model=None, top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents in the collection

        Args:
            query: Query string to search for
            embeddings_model: Embedding model to use for vectorization
            top_k: Number of top results to return

        Returns:
            List of dictionaries containing matched documents and their scores
        """
        if embeddings_model is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for embeddings")
            embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")

        try:
            # Create Qdrant instance for searching
            qdrant_store = Qdrant(
                client=self.client,
                collection_name=self.collection_name,
                embeddings=embeddings_model
            )

            # Perform similarity search
            results = qdrant_store.similarity_search_with_score(query, k=top_k)

            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "document": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                })

            logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results
        except Exception as e:
            logger.error(f"Search failed in collection '{self.collection_name}': {e}")
            raise

    def delete_collection(self):
        """
        Delete the collection from Qdrant
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to delete collection '{self.collection_name}': {e}")
            raise

    def get_collection_info(self):
        """
        Get information about the collection
        """
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": collection_info.config.params.vectors.size,
                "vector_size": collection_info.config.params.vectors.size,
                "count": collection_info.points_count,
                "config": collection_info.config.dict()
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for '{self.collection_name}': {e}")
            raise


# Singleton instance
_qdrant_instance = None

def get_qdrant_instance() -> QdrantVectorDB:
    """
    Get singleton instance of QdrantVectorDB
    """
    global _qdrant_instance
    if _qdrant_instance is None:
        _qdrant_instance = QdrantVectorDB()
    return _qdrant_instance