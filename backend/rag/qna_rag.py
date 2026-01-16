import logging
import hashlib
import os
from dotenv import load_dotenv
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_milvus import Milvus
from backend.embeddings import get_embeddings_client


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QnaRAG:
    def __init__(
        self, article_content: str, collection_name: str = "qna_rag_documents"
    ):
        self.article_content = article_content
        self.vector_store = Milvus(
            embedding_function=get_embeddings_client(),
            collection_name=collection_name,
            connection_args={
                "uri": (
                    f"http://{os.getenv('RAG_MILVUS_HOST', 'localhost')}:"
                    f"{os.getenv('RAG_MILVUS_PORT', '19530')}"
                ),
                "user": os.getenv("RAG_MILVUS_USER", ""),
                "password": os.getenv("RAG_MILVUS_PASSWORD", ""),
                "secure": os.getenv("RAG_MILVUS_SECURE", "false").lower() == "true",
            },
        )

    def index(self) -> str:
        """Index the article content into the vector store"""
        logger.info("Indexing content")

        # Generate hash of the article content
        article_hash = hashlib.sha256(self.article_content.encode("utf-8")).hexdigest()
        logger.info("Article hash: %s", article_hash)

        headers_to_split_on = [
            ("#", "h1"),
            ("##", "h2"),
        ]
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            return_each_line=False,
            strip_headers=False,
        )
        chunks = splitter.split_text(self.article_content)
        if not chunks:
            logger.warning("No document chunks created from content")
            raise ValueError("No document chunks created from content")

        logger.info("Split to %s document chunks", len(chunks))

        # Add article hash to each chunk's metadata
        for chunk in chunks:
            chunk.metadata["article_hash"] = article_hash

        try:
            logger.info("Attempting to index %s documents...", len(chunks))

            self.vector_store.add_documents(documents=chunks)
            logger.info("Documents added successfully")

        except Exception as e:
            logger.error("Error adding documents: %s", e)
            raise

        logger.info("Content indexed successfully")
        return article_hash

    def search(self, query: str, k: int = 2, article_hash: str = None):
        """Search for similar content in the vector store"""
        try:
            logger.info(
                "Searching collection '%s' for: %s...",
                self.vector_store.collection_name, query[:50]
            )

            # Try similarity search with score
            try:
                results = self.vector_store.similarity_search_with_score(query, k=k)
                logger.info("Raw search with score returned %s results", len(results))

                # Format results
                formatted_results = []
                for doc, score in results:
                    # Filter by article_hash if provided
                    if (
                        article_hash
                        and doc.metadata.get("article_hash") != article_hash
                    ):
                        continue

                    formatted_results.append(
                        {
                            "text": doc.page_content,
                            "score": score,
                            "metadata": doc.metadata,
                        }
                    )

            except Exception as e1:
                logger.warning(
                    "similarity_search_with_score failed: %s, trying basic search", e1
                )
                # Fallback to basic similarity search
                results = self.vector_store.similarity_search(query, k=k)
                logger.info("Raw basic search returned %s results", len(results))

                formatted_results = []
                for doc in results:
                    # Filter by article_hash if provided
                    if (
                        article_hash
                        and doc.metadata.get("article_hash") != article_hash
                    ):
                        continue

                    formatted_results.append(
                        {
                            "text": doc.page_content,
                            "score": 0.0,
                            "metadata": doc.metadata,
                        }
                    )

            logger.info(
                "Found %s results for query: %s...",
                len(formatted_results), query[:50]
            )
            return formatted_results

        except Exception as e:
            logger.error("Error during search: %s", e)
            return []
