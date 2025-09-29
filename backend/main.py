from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
import os

# Wczytanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Sprawdzenie, czy klucz API jest dostępny
if not os.getenv("GEMINI_API_KEY"):
    raise EnvironmentError("Brak klucza GEMINI_API_KEY w zmiennych środowiskowych!")

app = FastAPI(
    title="Personal AI Assistant API",
    description="Backend for planning and data processing using LLM."
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Asystent działa!"}

@app.get("/status")
def get_status():
    """Endpoint do sprawdzania statusu LLM (na razie proste testowe info)."""
    return {
        "llm_service": "Gemini/GCP",
        "database_vector": "ChromaDB (Local)",
        "ready": False,
        "note": "Potrzebna dalsza implementacja"
    }

# Opcjonalnie: Uruchomienie serwera bezpośrednio z pliku
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
