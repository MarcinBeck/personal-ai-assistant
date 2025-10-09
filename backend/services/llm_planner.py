import os
# Używamy tylko klienta Google do prostych kluczy API
from google import genai 
from google.genai import types
from backend.services.vector_db import VectorDBService
from dotenv import load_dotenv

# Wczytanie zmiennych środowiskowych z pliku .env
load_dotenv() 

class PlannerService:
    """
    Usługa integrująca ChromaDB z modelem Gemini. Używa klucza API (AI Studio).
    """
    
    def __init__(self):
        
        # Jawnie pobieramy klucz z ENV (ustawionego przez export lub .env)
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("Brak klucza GEMINI_API_KEY. Uzupełnij plik .env i ustaw w Bashu.")

        # Inicjalizacja klienta Gemini: 
        # Jawnie przekazujemy klucz, aby uniknąć problemów z ADC/OAuth2.
        self.client = genai.Client(api_key=api_key)
        
        self.db_service = VectorDBService() 
        self.model = 'gemini-2.5-flash'
        print(f"INFO: Uruchomiono serwis planowania z modelem {self.model}")

    def generate_daily_plan(self, current_date: str, additional_guidance: str = "") -> str:
        # LOGIKA RAG POZOSTAJE BEZ ZMIAN
        query = f"Podsumuj najważniejsze zadania, spotkania i zobowiązania z maili, które mają termin {current_date} lub w najbliższych dniach."
        retrieved_context = self.db_service.search_context(query, n_results=10)
        context_str = "\n".join([f"- {doc}" for doc in retrieved_context])
        
        system_prompt = (
            "Jesteś profesjonalnym asystentem planującym dzień pracy. Twoim zadaniem jest na podstawie "
            "dostarczonych informacji (maile, spotkania) i wytycznych wygenerowanie realistycznego planu dnia..."
        )
        
        user_prompt = (
            f"Oto kluczowe dane, które zebrałem na temat Twoich zobowiązań:\n\n"
            f"--- KONTEKST Z MAILI I SPOTKAŃ ---\n{context_str}\n"
            f"--- DODATKOWE WYTYCZNE NA DZIŚ ---\n{additional_guidance}\n\n"
            "Na podstawie powyższego, wygeneruj plan dnia w formacie listy numerowanej, podając szacowany czas trwania każdego bloku..."
        )
        
        config = types.GenerateContentConfig(temperature=0.5)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[system_prompt, user_prompt],
            config=config,
        )

        return response.text

if __name__ == '__main__':
    planner = PlannerService()
    guidance = "Dziś muszę zadzwonić do klienta X przed 12:00. Nie zapomnij o przeglądzie kalendarza na jutro."
    today = "2025-10-07"
    
    print("\n--- GENEROWANIE PLANU PRACY ---")
    
    try:
        daily_plan = planner.generate_daily_plan(current_date=today, additional_guidance=guidance)
        print(f"\nPLAN PRACY NA DZIEŃ {today}:\n")
        print(daily_plan)
    except Exception as e:
        print(f"\nBłąd podczas generowania planu: {e}")
        print("Jeśli widzisz 400 INVALID_ARGUMENT, klucz jest nieaktywny lub wymaga aktywacji rozliczeń Google.")