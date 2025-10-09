from pydantic import BaseModel
from datetime import datetime

class DocumentInput(BaseModel):
    """Model dla pojedynczego dokumentu wejściowego (email, transkrypcja, notatka)."""
    
    # Unikalny identyfikator dokumentu (np. ID maila, ID spotkania)
    doc_id: str
    
    # Pełna treść dokumentu (treść maila, transkrypcja)
    content: str
    
    # Typ źródła (np. 'email', 'calendar', 'transcription', 'note')
    source_type: str
    
    # Opcjonalny termin lub data, jeśli dokument go zawiera
    due_date: datetime = None
    
    # Dodatkowe metadane (np. nadawca, uczestnicy)
    metadata: dict = {}

class PlanningInput(BaseModel):
    """Model dla zapytania o plan dnia."""
    
    # Opcjonalne dodatkowe wytyczne dla LLM (np. "muszę zadzwonić")
    additional_guidance: str = ""
    
    # Data, dla której generujemy plan (domyślnie dziś)
    target_date: datetime = datetime.now()

class PlanEditInput(BaseModel):
    """Model dla edycji istniejącego planu."""
    existing_plan: str
    new_guidance: str