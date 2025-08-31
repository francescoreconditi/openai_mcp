# Chatbot with OpenAI and MCP Integration

Un'applicazione chatbot moderna costruita con Python, che integra OpenAI per l'intelligenza artificiale e un server MCP (Model Context Protocol) per estendere le capacità con tool personalizzati.

## 🚀 Caratteristiche Principali

- **Frontend Moderno**: Interfaccia chat Streamlit con cronologia delle conversazioni
- **Backend Scalabile**: Server FastAPI con validazione dati tramite Pydantic
- **Integrazione OpenAI**: Supporto completo per GPT-4 e altri modelli OpenAI
- **MCP Server**: Server di test con tool personalizzati pronti all'uso
- **Gestione Moderna**: Utilizza `uv` per la gestione delle dipendenze
- **Best Practices**: Codice strutturato, type hints, validazione dati

## 📁 Struttura del Progetto

```
chatbot-mcp/
├── src/
│   ├── backend/              # Backend FastAPI con integrazione OpenAI
│   │   ├── config.py         # Configurazione con Pydantic Settings
│   │   ├── models.py         # Modelli Pydantic per validazione
│   │   ├── openai_client.py  # Client OpenAI
│   │   ├── mcp_client.py     # Client per MCP server
│   │   ├── conversation_manager.py  # Gestione conversazioni
│   │   └── main.py           # Entry point FastAPI
│   │
│   ├── frontend/             # Frontend Streamlit
│   │   └── app.py            # Applicazione Streamlit
│   │
│   ├── mcp_server/           # MCP Server di test
│   │   ├── models.py         # Modelli per MCP
│   │   ├── tools.py          # Implementazione dei tool
│   │   └── server.py         # Server FastAPI per MCP
│   │
│   └── chatbot_mcp/          # Package principale
│       └── __init__.py
│
├── scripts/                  # Script di avvio
│   ├── run_backend.py        # Script per avviare il backend
│   ├── run_mcp_server.py     # Script per avviare MCP server
│   └── run_frontend.py       # Script per avviare il frontend
│
├── .env                      # File di configurazione (da creare)
├── .env.example             # Template configurazione
├── .gitignore               # File da ignorare in git
├── pyproject.toml           # Dipendenze e configurazione progetto
├── CLAUDE.md                # Guida per Claude Code
└── README.md                # Questo file
```

## 🛠️ Prerequisiti

- Python 3.11 o superiore
- uv (package manager moderno per Python)
- Account OpenAI con API key

## 🔧 Installazione

### 1. Clona il repository

```bash
git clone <repository-url>
```

### 2. Installa uv (se non già installato)

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Installa le dipendenze

```bash
uv sync
```

### 4. Configura le variabili d'ambiente

Crea un file `.env` nella directory `chatbot-mcp` copiando il template:

```bash
cp .env.example .env
```

Poi modifica il file `.env` aggiungendo la tua OpenAI API key:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx

# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001

# Backend Server Configuration
BACKEND_HOST=localhost
BACKEND_PORT=8000

# Model Configuration
MODEL_NAME=gpt-4o-mini
MAX_TOKENS=1000
TEMPERATURE=0.7
```

## 🚀 Avvio dell'Applicazione

L'applicazione richiede l'avvio di tre componenti separati. Apri tre terminali diverse:

### Terminal 1: MCP Server
```bash
uv run python scripts/run_mcp_server.py
```
Il server MCP sarà disponibile su http://localhost:8001

### Terminal 2: Backend Server
```bash
uv run python scripts/run_backend.py
```
Il backend sarà disponibile su http://localhost:8000

### Terminal 3: Frontend
```bash
uv run python scripts/run_frontend.py
```
Streamlit aprirà automaticamente il browser su http://localhost:8501

## 🔧 Tool MCP Disponibili

Il server MCP di test include i seguenti tool:

| Tool | Descrizione | Parametri |
|------|-------------|-----------|
| **get_current_time** | Ottiene data e ora corrente | `timezone` (opzionale) |
| **calculate** | Esegue calcoli matematici | `expression` (richiesto) |
| **get_random_number** | Genera numeri casuali | `min`, `max` (opzionali) |
| **convert_temperature** | Converte temperature | `value`, `from_unit`, `to_unit` |
| **get_weather** | Meteo simulato per demo | `city` (richiesto) |

## 🌐 API Endpoints

### Backend API (http://localhost:8000)

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| POST | `/chat` | Invia messaggio e ricevi risposta |
| GET | `/conversations` | Lista tutte le conversazioni |
| GET | `/conversations/{id}/messages` | Ottieni messaggi di una conversazione |
| DELETE | `/conversations/{id}` | Elimina una conversazione |
| GET | `/health` | Health check del servizio |
| GET | `/docs` | Documentazione interattiva Swagger |

### MCP Server API (http://localhost:8001)

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/tools` | Lista tool disponibili |
| POST | `/tools/execute` | Esegui un tool specifico |
| GET | `/tools/{name}` | Dettagli di un tool |
| GET | `/health` | Health check del servizio |
| GET | `/docs` | Documentazione interattiva Swagger |

## 🧪 Testing

### Eseguire i test
```bash
uv run pytest
```

### Verifica del codice
```bash
# Formattazione
uv run black src/

# Linting
uv run ruff check src/

# Type checking
uv run mypy src/
```

## 📖 Esempio di Utilizzo

1. **Avvia tutti i servizi** seguendo le istruzioni sopra

2. **Apri l'interfaccia Streamlit** nel browser

3. **Scrivi un messaggio** nella chat, ad esempio:
   - "Che ore sono?"
   - "Calcola 15 * 23 + 42"
   - "Converti 25 gradi Celsius in Fahrenheit"
   - "Genera un numero casuale tra 1 e 100"

4. **Osserva la risposta** che includerà:
   - La risposta dell'AI
   - I tool MCP utilizzati (se abilitati)
   - Timestamp delle interazioni

## ⚙️ Configurazione Avanzata

### Modificare il modello OpenAI
Nel file `.env`, cambia:
```env
MODEL_NAME=gpt-4  # oppure gpt-3.5-turbo, etc.
```

### Aggiungere nuovi tool MCP
Modifica `src/mcp_server/tools.py` e aggiungi nuovi metodi nella classe `ToolRegistry`.

### Personalizzare l'interfaccia
Modifica `src/frontend/app.py` per cambiare layout, colori e funzionalità.

## 🔍 Troubleshooting

### Errore: "Backend: Offline ❌"
- Verifica che il backend sia in esecuzione
- Controlla che la porta 8000 non sia già in uso

### Errore: "MCP Server: Offline ❌"
- Verifica che il MCP server sia in esecuzione
- Controlla che la porta 8001 non sia già in uso

### Errore OpenAI API
- Verifica che la API key sia corretta nel file `.env`
- Controlla di avere crediti sufficienti nel tuo account OpenAI

### Problemi con uv
- Assicurati di avere l'ultima versione: `uv self update`
- Prova a ricreare l'ambiente: `rm -rf .venv && uv sync`

## 📚 Documentazione Aggiuntiva

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [uv Documentation](https://github.com/astral-sh/uv)

## 🤝 Contribuire

1. Fork il progetto
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit dei cambiamenti (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📝 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

## 👤 Autori

- Francesco Reconditi

## 🙏 Ringraziamenti

- OpenAI per l'API GPT
- Streamlit per il framework UI
- FastAPI per il framework backend
- La community Python per gli strumenti eccellenti

---

**Nota**: Questo è un progetto di esempio per dimostrare l'integrazione tra OpenAI e MCP. I tool MCP forniti sono simulati e solo per scopo dimostrativo.