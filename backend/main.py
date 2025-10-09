from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv, dotenv_values 
from backend.models.data_models import DocumentInput, PlanningInput, PlanEditInput # Upewnij się, że PlanEditInput jest dodany
from backend.services.vector_db import VectorDBService
from backend.services.llm_planner import PlannerService

# Wczytanie zmiennych środowiskowych
load_dotenv()

# --- Weryfikacja kluczy ---
# Jawnie wczytujemy klucze dla startu aplikacji
config = dotenv_values(".env")
if not config.get("GEMINI_API_KEY"):
    raise EnvironmentError("Brak klucza GEMINI_API_KEY w pliku .env!")
# --- Koniec Weryfikacji ---


app = FastAPI(
    title="Personal AI Assistant API",
    description="Backend for planning and data processing using LLM."
)

# Inicjalizacja serwisów
# Uwaga: Te serwisy zostaną zainicjowane raz przy starcie aplikacji
db_service = VectorDBService()
planner_service = PlannerService()


@app.post("/data/ingest/text")
def ingest_text_data(content: str, doc_id: str, source_type: str = "manual_note"):
    """
    Przyjmuje czysty tekst i automatycznie indeksuje go do ChromaDB.
    Używane do szybkiego wklejania maili lub transkrypcji.
    """
    try:
        db_service.add_document(
            content=content, 
            source=source_type, 
            doc_id=doc_id
        )
        return {"status": "success", "doc_id": doc_id, "message": f"Dokument '{source_type}' zaindeksowany."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas indeksowania danych: {e}")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Asystent działa!"}

@app.get("/status")
def get_status():
    """Endpoint do sprawdzania statusu LLM i DB."""
    return {
        "status": "online",
        "llm_model": planner_service.model,
        "database_vector": "ChromaDB (Local)",
        "db_document_count": db_service.collection.count()
    }

@app.post("/data/ingest")
def ingest_data(doc: DocumentInput):
    """
    Przyjmuje dokument (mail/transkrypcję) i zapisuje go do bazy wektorowej.
    """
    try:
        # Metadane są używane do ułatwienia późniejszego zarządzania danymi
        metadata = {"source_type": doc.source_type, "metadata": doc.metadata}
        if doc.due_date:
            metadata['due_date'] = doc.due_date.isoformat()
            
        db_service.add_document(
            content=doc.content, 
            source=doc.source_type, 
            doc_id=doc.doc_id
        )
        return {"status": "success", "doc_id": doc.doc_id, "message": "Dokument zaindeksowany."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas indeksowania danych: {e}")


@app.post("/plan/generate")
def generate_plan(input_data: PlanningInput):
    """
    Generuje plan dnia na podstawie danych z bazy wektorowej i dodatkowych wytycznych.
    """
    try:
        # Formatowanie daty dla LLM
        target_date_str = input_data.target_date.strftime("%Y-%m-%d")
        
        daily_plan = planner_service.generate_daily_plan(
            current_date=target_date_str, 
            additional_guidance=input_data.additional_guidance
        )
        
        return {
            "status": "success", 
            "date": target_date_str, 
            "plan": daily_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd generowania planu: {e}")