"""
RAG-based long-term memory using ChromaDB. Stores conversation turns and
user facts, retrieves relevant context for each new message.
"""
import chromadb
from chromadb.utils import embedding_functions
import time


class LumisMemory:
    def __init__(self, persist_dir="./chroma_store", user_id="default_user"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.user_id = user_id
        self.collection = self.client.get_or_create_collection(
            name=f"lumis_memory_{user_id}", embedding_function=self.embedder
        )

    def add_turn(self, role: str, text: str, emotion: str = "Neutral"):
        doc_id = f"{self.user_id}_{int(time.time()*1000)}"
        self.collection.add(
            documents=[text],
            metadatas=[{"role": role, "emotion": emotion, "ts": time.time()}],
            ids=[doc_id],
        )

    def add_fact(self, fact: str, category: str = "preference"):
        doc_id = f"{self.user_id}_fact_{int(time.time()*1000)}"
        self.collection.add(
            documents=[fact],
            metadatas=[{"role": "fact", "category": category, "ts": time.time()}],
            ids=[doc_id],
        )

    def retrieve_context(self, query: str, k: int = 5):
        results = self.collection.query(query_texts=[query], n_results=k)
        if not results["documents"] or not results["documents"][0]:
            return []
        return list(zip(results["documents"][0], results["metadatas"][0]))

    def build_context_block(self, query: str, k: int = 5) -> str:
        memories = self.retrieve_context(query, k)
        if not memories:
            return "No prior relevant memory."
        lines = [f"- ({m['role']}, emotion={m.get('emotion','n/a')}): {doc}" for doc, m in memories]
        return "RETRIEVED MEMORY:\n" + "\n".join(lines)
