"""
RAG Engine: Vector Database Management & Policy Retrieval via ChromaDB.
"""

import os
from typing import Any, Dict, List, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import settings


class PolicyVectorStore:
    def __init__(self):
        # Universal attribute fallback to prevent AttributeError
        self.persist_directory = getattr(
            settings, "PERSIST_DIRECTORY", getattr(settings, "CHROMA_PERSIST_DIR", "./data/chroma_db")
        )
        self.embedding_function = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME
        )
        self.db: Optional[Chroma] = None

    def initialize_db(self, pdf_path: Optional[str] = None):
        if pdf_path is None:
            pdf_path = getattr(settings, "DOCUMENT_SOURCE_PATH", "./data/qatar_sla_policy.pdf")

        if not os.path.exists(pdf_path):
            print(f"[RAG Alert] Policy file not found at '{pdf_path}'. Initializing empty store.")
            self.db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function,
            )
            return

        print(f"[RAG] Ingesting policy document: {pdf_path}...")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        self.db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_function,
            persist_directory=self.persist_directory,
        )
        print(f"[RAG Success] Successfully indexed {len(chunks)} SLA/Policy chunks into ChromaDB.")

    def retrieve_relevant_policy(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        if self.db is None:
            self.db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function,
            )

        results = self.db.similarity_search_with_score(query, k=top_k)

        extracted_chunks = []
        for doc, score in results:
            extracted_chunks.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": float(score),
            })

        return extracted_chunks


if __name__ == "__main__":
    vs = PolicyVectorStore()
    vs.initialize_db()