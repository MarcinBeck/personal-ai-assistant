import os
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from typing import List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Stałe dla ChromaDB (używane lokalnie)
CHROMA_PATH = os.path.join(os.getcwd(), "chroma_data")
COLLECTION_NAME = "work_context"

# Wczytujemy URL bazy danych
DATABASE_URL = os.getenv("DATABASE_URL")

# --- Funkcja Osadzania ---
# Używamy tej samej funkcji dla obu baz danych
EMBEDDING_FUNCTION = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


class VectorDBService:
    """
    Usługa zarządzająca bazą wektorową, obsługująca ChromaDB (dev) i PostgreSQL (prod).
    """

    def __init__(self):
        # 1. Próba połączenia z PostgreSQL
        if DATABASE_URL:
            try:
                self.engine = create_engine(DATABASE_URL)
                with self.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                print(f"INFO: Uruchomiono bazę PRODUKCYJNĄ (PostgreSQL)")
                self.mode = 'postgres'
                # W środowisku prod, będziemy używać pgvector (pomijamy implementację tablek, na razie tylko test połączenia)
                return 
            except OperationalError:
                print("OSTRZEŻENIE: Błąd połączenia z PostgreSQL. Przechodzę do trybu ChromaDB.")
        
        # 2. Domyślne użycie ChromaDB (Tryb Deweloperski)
        self.client = PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=EMBEDDING_FUNCTION
        )
        print(f"INFO: Uruchomiono bazę DEWELOPERSKĄ (ChromaDB) w folderze: {CHROMA_PATH}")
        self.mode = 'chroma'
    
    
    def get_embedding(self, content: str):
        """Generuje wektor na podstawie treści."""
        return EMBEDDING_FUNCTION([content])[0]

    def add_document(self, content: str, source: str, doc_id: str):
        """Dodaje dokument do aktywnej bazy danych."""
        if self.mode == 'postgres':
            # W przyszłości: zapis metadanych do tabeli SQL i wektora do pgvector
            print(f"Zapis do PG: {doc_id} - [TODO: Implementacja pgvector]")
        else: # ChromaDB
            self.collection.add(
                documents=[content],
                metadatas=[{"source": source}],
                ids=[doc_id]
            )
        return True

    def search_context(self, query: str, n_results: int = 5) -> List[str]:
        """Wyszukuje najbardziej podobne konteksty."""
        if self.mode == 'postgres':
            # W przyszłości: Zapytanie do pgvector
            return [f"Wynik z PG dla: {query} [TODO: Implementacja pgvector]"]
        else: # ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents']
            )
            return [doc for docs in results.get('documents', []) for doc in docs]

# Przykład użycia (usuń, aby uniknąć problemów z Uvicorn)
# if __name__ == '__main__': ...