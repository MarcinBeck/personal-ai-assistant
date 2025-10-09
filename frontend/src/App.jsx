import React, { useState } from 'react';
import DataIngest from './DataIngest'; // Import nowego komponentu
import './App.css';

const API_BASE_URL = '/api';

function App() {
  const [guidance, setGuidance] = useState('');
  const [plan, setPlan] = useState('Brak planu. Wprowadź wytyczne i wygeneruj plan dnia.');
  const [loading, setLoading] = useState(false);
  const [dbCount, setDbCount] = useState(null); // Nowy stan do przechowywania liczby dokumentów

  // Domyślna data do planowania (jutro)
  const today = new Date().toISOString().substring(0, 10);
  const tomorrow = new Date(new Date().getTime() + (24 * 60 * 60 * 1000)).toISOString().substring(0, 10);
  const [targetDate, setTargetDate] = useState(tomorrow);


  // Funkcja do pobierania liczby dokumentów z Backendu
  const fetchDbCount = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/status`);
        if (response.ok) {
            const data = await response.json();
            setDbCount(data.db_document_count);
        }
    } catch (error) {
        console.error("Nie udało się pobrać statusu DB:", error);
    }
  };

  // Ładujemy licznik dokumentów przy starcie
  React.useEffect(() => {
    fetchDbCount();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;

    setLoading(true);
    setPlan('Generowanie planu przez Gemini... Proszę czekać...');

    try {
      const response = await fetch(`${API_BASE_URL}/plan/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          additional_guidance: guidance,
          target_date: targetDate, 
        }),
      });

      if (!response.ok) {
        throw new Error(`Błąd serwera: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setPlan(data.plan.trim()); 

    } catch (error) {
      setPlan(`Błąd generowania planu: ${error.message}`);
      console.error('Błąd:', error);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="container">
      <h1>🤖 Osobisty Asystent AI</h1>
      <p className="subtitle">
        Status DB: <strong>{dbCount !== null ? `${dbCount} dokumentów zindeksowanych` : 'Ładowanie...'}</strong>
      </p>
      
      {/* 1. SEKCJA WPROWADZANIA DANYCH */}
      <DataIngest onIngestSuccess={fetchDbCount} /> 

      {/* 2. SEKCJA GENEROWANIA PLANU */}
      <div className="card plan-controls">
        <h2>Wygeneruj Plan Dnia</h2>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="date">Data Planowania:</label>
            <input 
              type="date" 
              id="date" 
              value={targetDate} 
              onChange={(e) => setTargetDate(e.target.value)} 
            />
          </div>
          
          <div className="input-group">
            <label htmlFor="guidance">Dodatkowe Wytyczne / Edycja Istniejącego Planu:</label>
            <textarea
              id="guidance"
              value={guidance}
              onChange={(e) => setGuidance(e.target.value)}
              placeholder="Wprowadź nowe wytyczne, np. 'Muszę przesunąć telefon o 30 minut' albo 'Dodaj nowe zadanie: Podsumowanie projektu Z'."
              rows="4"
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Generowanie...' : 'Wygeneruj/Modyfikuj Plan Dnia'}
          </button>
        </form>
      </div>

      {/* 3. SEKCJA WYNIKÓW */}
      <div className="card plan-output">
        <h2>🗓️ Plan Pracy ({targetDate})</h2>
        <pre className="plan-text">
          {plan}
        </pre>
      </div>
      
      <p className="footer-note">
        * Plan bazuje na: 1) Zindeksowanych mailach/spotkaniach (ChromaDB) i 2) Powyższych wytycznych.
      </p>
    </div>
  );
}

export default App;