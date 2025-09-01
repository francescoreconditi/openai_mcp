# Chatbot with OpenAI and MCP Integration

Un'applicazione chatbot moderna costruita con Python, che integra OpenAI per l'intelligenza artificiale e un server MCP (Model Context Protocol) per estendere le capacità con tool personalizzati.

## 🚀 Caratteristiche Principali

- **Doppio Frontend**: 
  - **Streamlit**: Interfaccia rapida per prototipazione
  - **React**: Interfaccia moderna e responsiva con registrazione vocale
- **Registrazione Vocale**: Funzionalità di voice input con trascrizione automatica
- **Backend Scalabile**: Server FastAPI con validazione dati tramite Pydantic
- **Integrazione OpenAI**: Supporto completo per GPT-4 e altri modelli OpenAI + Whisper per trascrizione
- **FastMCP Integration**: Server MCP compatibile con standard FastMCP
- **Doppia Compatibilità**: Supporta sia il backend interno che client esterni come Claude
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
│   ├── frontend/             # Frontend Streamlit (legacy)
│   │   ├── app.py            # Applicazione Streamlit
│   │   └── audio_transcriber.py  # Gestione trascrizione audio
│   │
│   ├── frontend_react/       # Frontend React (moderno)
│   │   ├── src/
│   │   │   ├── components/   # Componenti React
│   │   │   ├── services/     # Servizi API
│   │   │   ├── styles/       # Stili CSS
│   │   │   ├── App.js        # Componente principale
│   │   │   └── index.js      # Entry point
│   │   ├── public/
│   │   ├── package.json      # Dipendenze npm
│   │   └── README.md         # Documentazione React
│   │
│   ├── mcp_server/           # MCP Server (compatibile FastMCP)
│   │   ├── models.py         # Modelli per MCP
│   │   ├── tools.py          # Implementazione dei tool (legacy)
│   │   ├── server.py         # Server FastAPI originale
│   │   ├── fastmcp_server.py # Server FastMCP standard
│   │   └── hybrid_server.py  # Server ibrido (FastMCP + REST)
│
├── scripts/                  # Script di avvio
│   ├── run_backend.py        # Script per avviare il backend
│   ├── run_backend_subprocess.py # Backend con MCP integrato
│   ├── run_mcp_server.py     # Script per avviare MCP server originale
│   ├── run_hybrid_mcp.py     # Script per server ibrido (RACCOMANDATO)
│   ├── run_fastmcp_server.py # Script per FastMCP puro (per Claude)
│   ├── run_fastmcp_http.py   # Script per FastMCP HTTP
│   ├── run_frontend.py       # Script per frontend Streamlit
│   └── run_frontend_react.py # Script per frontend React
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
- Node.js 16+ e npm (per frontend React)
- Account OpenAI con API key (incluso Whisper per trascrizione vocale)
- FastMCP per la compatibilità con client MCP standard

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

L'applicazione supporta diverse modalità di avvio:

### 🚀 Modalità Ultra-Semplice (MCP Subprocess) - NUOVA!
**Solo 2 processi invece di 3!** Il server MCP viene avviato automaticamente come subprocess:

#### Frontend Streamlit (legacy)
```bash
# Terminal 1: Backend con MCP integrato (porta 8000)
uv run python scripts/run_backend_subprocess.py

# Terminal 2: Frontend Streamlit (porta 8501) 
uv run python scripts/run_frontend.py
```

#### Frontend React (raccomandato)
```bash
# Terminal 1: Backend con MCP integrato (porta 8000)
uv run python scripts/run_backend_subprocess.py

# Terminal 2: Frontend React (porta 3000)
uv run python scripts/run_frontend_react.py
```

**Vantaggi:**
- ✅ MCP server avviato automaticamente
- ✅ Un processo in meno da gestire
- ✅ Stesso server MCP compatibile con Claude Desktop
- ✅ Comunicazione diretta via stdio (più efficiente)
- ✅ Frontend React con registrazione vocale avanzata

### 🔥 Modalità Server Separato (Universale)
Per controllo completo sui transport MCP:

```bash
# Terminal 1: Server Universale MCP (porta 8001)
uv run python scripts/run_universal_mcp.py --transport hybrid

# Terminal 2: Backend Server (porta 8000)
uv run python scripts/run_backend.py

# Terminal 3: Frontend Streamlit (porta 8501) o React (porta 3000)
uv run python scripts/run_frontend.py        # Streamlit
uv run python scripts/run_frontend_react.py  # React
```

**Opzioni transport:**
- `--transport stdio` - Per Claude Desktop (default)
- `--transport sse` - Solo SSE, MCP puro (NO REST endpoints)
- `--transport hybrid` - REST + SSE (RICHIESTO per il backend)

### 🏛️ Modalità Legacy (Server Originale)
Per compatibilità con la versione precedente:

```bash
# Terminal 1: Server MCP Originale (porta 8001)
uv run python scripts/run_mcp_server.py

# Terminal 2: Backend Server (porta 8000)
uv run python scripts/run_backend.py

# Terminal 3: Frontend Streamlit (porta 8501) o React (porta 3000)
uv run python scripts/run_frontend.py        # Streamlit  
uv run python scripts/run_frontend_react.py  # React
```

### 🤖 Modalità Solo Claude (FastMCP Puro)
Per integrazione diretta con Claude Desktop:

```bash
# Server FastMCP con protocollo stdio (per Claude)
uv run python scripts/run_fastmcp_server.py
```

> **Nota**: La modalità solo Claude non supporta il backend web. È pensata per integrazione diretta con client MCP come Claude Desktop.

## 📊 Confronto Modalità

| Modalità | Processi | MCP Protocol | OpenAI | Claude | Frontend | Complessità |
|----------|----------|--------------|--------|---------|----------|-------------|
| **Subprocess** | 2 | stdio | ✅ | ✅ | Streamlit/React | ⭐ Semplice |
| **Universale** | 3 | stdio/sse/http | ✅ | ✅ | Streamlit/React | ⭐⭐ Media |
| **Legacy** | 3 | REST only | ✅ | ❌ | Streamlit/React | ⭐⭐ Media |
| **Solo Claude** | 1 | stdio | ❌ | ✅ | Nessuno | ⭐ Semplice |

## 🤖 Integrazione con Claude Desktop

### Opzione 1: Server Universale (stdio)
```bash
# Avvia in modalità stdio per Claude
uv run python scripts/run_universal_mcp.py --transport stdio
```

### Opzione 2: Configurazione automatica
Aggiungi al file di configurazione Claude Desktop:
```json
{
  "mcpServers": {
    "chatbot-tools": {
      "command": "uv",
      "args": ["run", "python", "scripts/run_universal_mcp.py", "--transport", "stdio"],
      "cwd": "/path/to/chatbot-mcp"
    }
  }
}
```

### Opzione 3: HTTP Streaming (futuro)
Quando Claude Desktop supporterà HTTP streaming:
```bash
# Server con SSE (MCP standard HTTP transport)
uv run python scripts/run_universal_mcp.py --transport sse --port 8001
```

> **Nota**: Attualmente Claude Desktop supporta solo stdio, ma il server è pronto per HTTP streaming quando sarà disponibile.

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

2. **Apri l'interfaccia** nel browser:
   - **Streamlit**: http://localhost:8501
   - **React**: http://localhost:3000

3. **Scrivi un messaggio o usa la registrazione vocale** nella chat, ad esempio:
   - "Che ore sono?"
   - "Calcola 15 * 23 + 42"
   - "Converti 25 gradi Celsius in Fahrenheit"
   - "Genera un numero casuale tra 1 e 100"
   - **🎤 Registra vocalmente** il tuo messaggio (solo React)

4. **Osserva la risposta** che includerà:
   - La risposta dell'AI
   - I tool MCP utilizzati (se abilitati)
   - Timestamp delle interazioni
   - **Trascrizione vocale** se utilizzata

## ⚙️ Configurazione Avanzata

### Modificare il modello OpenAI
Nel file `.env`, cambia:
```env
MODEL_NAME=gpt-4  # oppure gpt-3.5-turbo, etc.
```

### Aggiungere nuovi tool MCP

**Per il server ibrido FastMCP (raccomandato):**
Modifica `src/mcp_server/fastmcp_server.py` e aggiungi nuove funzioni con il decorator `@mcp.tool()`:

```python
@mcp.tool()
def my_new_tool(param1: str, param2: int = 42) -> str:
    """Descrizione del mio nuovo tool.
    
    Args:
        param1: Primo parametro (richiesto)
        param2: Secondo parametro (opzionale, default: 42)
        
    Returns:
        Risultato del tool
    """
    return f"Risultato: {param1} + {param2}"
```

**Per il server legacy:**
Modifica `src/mcp_server/tools.py` e aggiungi nuovi metodi nella classe `ToolRegistry`.

### Personalizzare l'interfaccia

**Frontend Streamlit:**
Modifica `src/frontend/app.py` per cambiare layout, colori e funzionalità.

**Frontend React:**
- Componenti: `src/frontend_react/src/components/`
- Stili: `src/frontend_react/src/styles/`
- Servizi API: `src/frontend_react/src/services/`

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
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Guida MCP e OpenAI](docs/mcp-openai-guide.md)

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