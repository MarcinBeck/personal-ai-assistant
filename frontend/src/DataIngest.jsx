import React, { useState } from 'react';

const API_BASE_URL = '/api';

function DataIngest({ onIngestSuccess }) {
    const [content, setContent] = useState('');
    const [docType, setDocType] = useState('email');
    const [status, setStatus] = useState('');
    const [loading, setLoading] = useState(false);

    const generateId = () => `${docType}-${Date.now()}`;

    const handleIngest = async (e) => {
        e.preventDefault();
        if (!content || loading) return;

        setLoading(true);
        setStatus('Indeksowanie danych...');

        try {
            const docId = generateId();
            
            const params = new URLSearchParams({
                content: content,
                doc_id: docId,
                source_type: docType,
            });

            const response = await fetch(`${API_BASE_URL}/data/ingest/text?${params.toString()}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, // Ustawiamy odpowiedni Content-Type
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Błąd serwera podczas indeksowania.');
            }

            setStatus(`✅ Sukces! Dokument (${docId}) zaindeksowany. Teraz możesz wygenerować plan.`);
            setContent(''); // Wyczyść pole po sukcesie
            
            // Opcjonalny callback do odświeżenia statusu w App.jsx
            if(onIngestSuccess) onIngestSuccess();

        } catch (error) {
            setStatus(`❌ Błąd: ${error.message}`);
            console.error('Ingest Error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card ingest-controls">
            <h2>📥 Ręczne Zasilanie Danych</h2>
            <p className="status-message">{status}</p>

            <form onSubmit={handleIngest}>
                <div className="input-group">
                    <label htmlFor="docType">Typ Danych:</label>
                    <select id="docType" value={docType} onChange={(e) => setDocType(e.target.value)}>
                        <option value="email">E-mail</option>
                        <option value="transcription">Transkrypcja Spotkania</option>
                        <option value="note">Notatka/Wytyczna</option>
                    </select>
                </div>

                <div className="input-group">
                    <label htmlFor="content">Wklej Całą Treść (E-mail/Transkrypcja):</label>
                    <textarea
                        id="content"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="Wklej tutaj treść maila lub transkrypcji..."
                        rows="6"
                    />
                </div>

                <button type="submit" disabled={loading}>
                    {loading ? 'Indeksowanie...' : 'Zaindeksuj Dane (Zapisz do DB)'}
                </button>
            </form>
        </div>
    );
}

export default DataIngest;