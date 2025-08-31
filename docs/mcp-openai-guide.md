# Guida Completa: MCP (Model Context Protocol) e OpenAI Integration

Una guida pratica per comprendere e utilizzare il Model Context Protocol con OpenAI per estendere le capacità dell'AI con tool personalizzati.

## 📋 Indice

1. [Introduzione a MCP](#introduzione-a-mcp)
2. [Perché usare MCP con OpenAI](#perché-usare-mcp-con-openai)
3. [Architettura del Sistema](#architettura-del-sistema)
4. [Implementazione Pratica](#implementazione-pratica)
5. [FastMCP vs MCP Standard](#fastmcp-vs-mcp-standard)
6. [Esempi di Tool](#esempi-di-tool)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## 🚀 Introduzione a MCP

Il **Model Context Protocol (MCP)** è uno standard aperto per estendere le capacità di modelli di AI attraverso tool personalizzati. Permette di:

- **Eseguire codice** in contesti controllati
- **Accedere a API esterne** (database, servizi web, ecc.)
- **Manipolare file** e dati locali
- **Integrare sistemi esistenti** senza modifiche

### Vantaggi Chiave

| Vantaggio | Descrizione |
|-----------|-------------|
| **Standardizzazione** | Protocollo comune per tutti i client AI |
| **Sicurezza** | Controllo granulare sui permessi dei tool |
| **Scalabilità** | Aggiunta di nuovi tool senza modificare il client |
| **Interoperabilità** | Compatibilità con Claude, OpenAI, e altri |

## 🤔 Perché usare MCP con OpenAI

OpenAI supporta **Function Calling** ma con limitazioni:

### Function Calling OpenAI (Tradizionale)
```json
{
  "functions": [{
    "name": "get_weather", 
    "description": "Get weather data",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {"type": "string"}
      }
    }
  }]
}
```

❌ **Limitazioni:**
- Definizioni hardcoded nel codice
- Difficile condivisione tra progetti
- Nessuna standardizzazione

### MCP + OpenAI (Moderno)
```python
@mcp.tool()
def get_weather(city: str) -> dict:
    """Get weather for a city"""
    return fetch_weather_api(city)
```

✅ **Vantaggi:**
- Tool riusabili e modulari
- Standard comune
- Facilmente condivisibile con Claude
- Auto-discovery dei tool

## 🏗️ Architettura del Sistema

### Panoramica
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   MCP Server    │
│   (Streamlit)   │───▶│   (FastAPI)     │───▶│   (FastMCP)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   OpenAI API    │    │   Tool Executor │
                       │                 │    │                 │
                       └─────────────────┘    └─────────────────┘
```

### Flusso di Esecuzione

1. **User Input** → Frontend riceve messaggio utente
2. **Backend Processing** → Backend chiede tool disponibili al server MCP
3. **OpenAI Request** → Backend invia messaggio + tool definitions ad OpenAI
4. **Function Call** → OpenAI richiede esecuzione tool (se necessario)
5. **Tool Execution** → Backend esegue tool tramite MCP server
6. **Final Response** → OpenAI genera risposta finale con risultati tool

### Componenti Dettagliati

#### 🎯 **Backend (FastAPI)**
- **Orchestrazione**: Coordina frontend, OpenAI, e MCP
- **Conversation Management**: Mantiene cronologia chat
- **Tool Integration**: Converte MCP tools → OpenAI function format

#### 🔧 **MCP Server (FastMCP)**  
- **Tool Registry**: Catalogo automatico dei tool disponibili
- **Execution Engine**: Esecuzione sicura dei tool
- **Schema Generation**: Auto-generazione schemi JSON per OpenAI

#### 🤖 **OpenAI Integration**
- **Function Calling**: Richiesta tool quando necessario
- **Context Management**: Mantiene contesto conversazione
- **Error Handling**: Gestione errori tool execution

## 💻 Implementazione Pratica

### 1. Definizione Tool con FastMCP

```python
from fastmcp import FastMCP

mcp = FastMCP("My Tools Server")

@mcp.tool()
def calculate(expression: str) -> float:
    """Perform mathematical calculations.
    
    Args:
        expression: Mathematical expression (e.g., "2+2*3")
        
    Returns:
        Calculation result
        
    Raises:
        ValueError: If expression is invalid
    """
    try:
        # Secure evaluation with limited builtins
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

@mcp.tool()
def get_system_info() -> dict:
    """Get system information."""
    import platform
    import psutil
    
    return {
        "platform": platform.system(),
        "version": platform.version(),
        "cpu_count": psutil.cpu_count(),
        "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk_usage": psutil.disk_usage('/').percent
    }
```

### 2. Server Ibrido (FastMCP + REST API)

```python
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("Tools")

# Tool definitions (come sopra)

@app.get("/tools")
async def get_tools():
    """REST endpoint per backend compatibility"""
    fastmcp_tools = await mcp.get_tools()
    
    # Converti formato FastMCP → OpenAI
    openai_tools = []
    for name, tool in fastmcp_tools.items():
        # Estrai schema da function signature
        schema = generate_schema_from_function(tool.fn)
        openai_tools.append({
            "name": name,
            "description": tool.description,
            "parameters": schema
        })
    
    return openai_tools

@app.post("/tools/execute")  
async def execute_tool(request: ToolRequest):
    """Esegui tool e restituisci risultato"""
    try:
        result = await execute_fastmcp_tool(request.name, request.arguments)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
```

### 3. Integrazione Backend

```python
class OpenAIClient:
    async def generate_response(self, messages, tools=None):
        kwargs = {
            "model": "gpt-4o-mini",
            "messages": messages
        }
        
        # Aggiungi tool se disponibili
        if tools:
            kwargs["tools"] = self.convert_to_openai_format(tools)
            kwargs["tool_choice"] = "auto"
        
        response = await self.client.chat.completions.create(**kwargs)
        
        # Gestisci tool calls
        if response.choices[0].message.tool_calls:
            return await self.handle_tool_calls(
                response.choices[0].message.tool_calls
            )
        
        return response.choices[0].message.content

    def convert_to_openai_format(self, mcp_tools):
        """Converte MCP tools → OpenAI function format"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"], 
                    "parameters": tool["parameters"]
                }
            }
            for tool in mcp_tools
        ]
```

## ⚖️ FastMCP vs MCP Standard

### FastMCP (Raccomandato)

```python
from fastmcp import FastMCP

mcp = FastMCP("Server Name")

@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description"""
    return f"Result: {param}"

# Avvio automatico
mcp.run(transport="stdio")  # Per Claude
mcp.run(transport="sse", port=8001)  # Per HTTP
```

✅ **Pro:**
- Setup minimo
- Auto-discovery tool
- Compatibilità Claude nativa
- Type hints automatici
- Documentazione auto-generata

❌ **Contro:**
- Meno controllo granulare
- Dipendenza esterna

### MCP Standard (Manual)

```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
        
    def register_tool(self, name, func, schema):
        self.tools[name] = {
            "function": func,
            "schema": schema
        }
        
    async def execute(self, name, args):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        return await self.tools[name]["function"](**args)
```

✅ **Pro:**
- Controllo completo
- Nessuna dipendenza
- Customizzazione totale

❌ **Contro:**
- Più codice boilerplate
- Schema manuali
- Nessuna standardizzazione

## 🛠️ Esempi di Tool

### Tool per Database

```python
@mcp.tool()
async def query_database(query: str, limit: int = 10) -> list:
    """Execute SQL query on database.
    
    Args:
        query: SQL SELECT query
        limit: Maximum rows to return
        
    Returns:
        Query results as list of dicts
    """
    import asyncpg
    
    # Validazione query (solo SELECT)
    if not query.strip().upper().startswith('SELECT'):
        raise ValueError("Only SELECT queries allowed")
    
    conn = await asyncpg.connect("postgresql://...")
    try:
        results = await conn.fetch(query)
        return [dict(row) for row in results[:limit]]
    finally:
        await conn.close()
```

### Tool per File System

```python
@mcp.tool()
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """Read file content.
    
    Args:
        file_path: Path to file to read
        encoding: File encoding (default: utf-8)
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If no read access
    """
    import os
    from pathlib import Path
    
    # Sicurezza: solo file nella directory consentita
    allowed_dir = Path("/safe/directory")
    file_path = Path(file_path).resolve()
    
    if not file_path.is_relative_to(allowed_dir):
        raise PermissionError("File access denied")
    
    return file_path.read_text(encoding=encoding)

@mcp.tool()
def list_directory(dir_path: str, pattern: str = "*") -> list:
    """List files in directory.
    
    Args:
        dir_path: Directory path to list
        pattern: Glob pattern for filtering (default: all files)
        
    Returns:
        List of file/directory names
    """
    from pathlib import Path
    
    dir_path = Path(dir_path)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory {dir_path} not found")
    
    return [item.name for item in dir_path.glob(pattern)]
```

### Tool per API Esterne

```python
@mcp.tool()
async def get_weather(city: str, units: str = "metric") -> dict:
    """Get weather information for a city.
    
    Args:
        city: City name
        units: Temperature units (metric/imperial/kelvin)
        
    Returns:
        Weather data dictionary
    """
    import httpx
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("Weather API key not configured")
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": units
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data.get("wind", {}).get("speed", 0)
        }
```

### Tool per Git Operations

```python
@mcp.tool()
def git_status(repo_path: str = ".") -> dict:
    """Get git repository status.
    
    Args:
        repo_path: Path to git repository (default: current directory)
        
    Returns:
        Git status information
    """
    import subprocess
    from pathlib import Path
    
    repo_path = Path(repo_path).resolve()
    
    try:
        # Git status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse output
        changes = []
        for line in result.stdout.strip().split('\n'):
            if line:
                status = line[:2]
                file_path = line[3:]
                changes.append({
                    "status": status.strip(),
                    "file": file_path
                })
        
        return {
            "repository": str(repo_path),
            "changes": changes,
            "clean": len(changes) == 0
        }
        
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Git command failed: {e}")
```

## 📏 Best Practices

### 🔒 Sicurezza

1. **Validazione Input Rigorosa**
```python
@mcp.tool()
def secure_execute(command: str) -> str:
    """Execute safe commands only."""
    
    # Whitelist comandi consentiti
    allowed_commands = ["ls", "pwd", "date", "whoami"]
    
    if command.split()[0] not in allowed_commands:
        raise ValueError(f"Command '{command}' not allowed")
    
    return subprocess.run(command, shell=True, capture_output=True, text=True).stdout
```

2. **Limitazione Risorse**
```python
@mcp.tool()
async def limited_request(url: str) -> dict:
    """Make HTTP request with limits."""
    
    timeout = httpx.Timeout(10.0)  # 10 second timeout
    limits = httpx.Limits(max_connections=5)
    
    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        response = await client.get(url)
        
        # Limita dimensione risposta
        if len(response.content) > 1_000_000:  # 1MB
            raise ValueError("Response too large")
            
        return response.json()
```

### 📊 Error Handling

```python
@mcp.tool()
def robust_tool(data: str) -> dict:
    """Tool with comprehensive error handling."""
    
    try:
        # Validazione input
        if not data or not isinstance(data, str):
            raise ValueError("Data must be a non-empty string")
        
        # Elaborazione
        result = process_data(data)
        
        # Validazione output
        if not result:
            raise RuntimeError("Processing failed to produce result")
            
        return {"success": True, "result": result}
        
    except ValueError as e:
        # Errori di validazione
        return {"success": False, "error": f"Validation error: {e}"}
        
    except Exception as e:
        # Errori generici
        logger.error(f"Tool execution failed: {e}")
        return {"success": False, "error": "Internal processing error"}
```

### 📝 Documentazione

```python
@mcp.tool()
def well_documented_tool(
    input_data: str,
    options: dict = None,
    timeout: int = 30
) -> dict:
    """Process input data with configurable options.
    
    This tool demonstrates comprehensive documentation for MCP tools.
    It processes text input with various configuration options.
    
    Args:
        input_data: Text data to process. Must be non-empty string.
        options: Optional configuration dict. Supported keys:
            - format: Output format ("json" | "text" | "xml")  
            - encoding: Text encoding (default: "utf-8")
            - compress: Whether to compress output (default: False)
        timeout: Processing timeout in seconds (default: 30, max: 300)
        
    Returns:
        Processing result dict with structure:
        {
            "success": bool,
            "result": str | dict,
            "metadata": {
                "processing_time": float,
                "input_size": int,
                "output_size": int
            }
        }
        
    Raises:
        ValueError: If input_data is empty or invalid
        TimeoutError: If processing exceeds timeout
        RuntimeError: If processing fails
        
    Examples:
        >>> tool("hello world")
        {"success": True, "result": "HELLO WORLD", "metadata": {...}}
        
        >>> tool("data", {"format": "json"})  
        {"success": True, "result": {"processed": "DATA"}, ...}
    """
    # Implementazione...
```

### ⚡ Performance

```python
@mcp.tool()
async def optimized_tool(items: list) -> list:
    """Process items with performance optimizations."""
    
    # Batch processing per grandi dataset
    if len(items) > 1000:
        batch_size = 100
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            batch_result = await process_batch(batch)
            results.extend(batch_result)
            
            # Yield control per evitare blocking
            await asyncio.sleep(0)
            
        return results
    
    # Processing normale per piccoli dataset
    return await process_items(items)

# Caching per risultati costosi
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_computation(input_hash: str) -> str:
    """Expensive computation with caching."""
    return expensive_function(input_hash)

@mcp.tool()
def smart_compute(data: str) -> str:
    """Compute with intelligent caching."""
    import hashlib
    
    # Hash input per cache key
    data_hash = hashlib.md5(data.encode()).hexdigest()
    return cached_computation(data_hash)
```

## 🐛 Troubleshooting

### Problemi Comuni

#### 1. Tool Non Riconosciuti
```bash
# Verifica tool disponibili
curl http://localhost:8001/tools

# Debug server MCP
uv run python scripts/run_hybrid_mcp.py --debug
```

#### 2. Errori di Esecuzione Tool
```python
# Aggiungi logging dettagliato
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@mcp.tool()
def debug_tool(data: str) -> str:
    logger.debug(f"Tool called with: {data}")
    try:
        result = process(data)
        logger.debug(f"Tool result: {result}")
        return result
    except Exception as e:
        logger.error(f"Tool failed: {e}", exc_info=True)
        raise
```

#### 3. Timeout Issues
```python
# Configurazione timeout personalizzata
import asyncio

@mcp.tool()
async def long_running_tool(data: str) -> str:
    """Tool with custom timeout handling."""
    
    try:
        # Timeout personalizzato per operazione specifica
        return await asyncio.wait_for(
            slow_operation(data),
            timeout=60.0  # 60 secondi
        )
    except asyncio.TimeoutError:
        raise RuntimeError("Operation timed out after 60 seconds")
```

#### 4. Schema Validation Errors
```python
# Debug schema generation
@mcp.tool()
def schema_debug_tool(param: str) -> dict:
    """Tool for debugging schema issues.
    
    Args:
        param: Input parameter with clear type
        
    Returns:
        Clear return type specification
    """
    return {"input": param, "type": type(param).__name__}

# Verifica schema generato
import json
from src.mcp_server.fastmcp_server import mcp

async def debug_schemas():
    tools = await mcp.get_tools()
    for name, tool in tools.items():
        print(f"\n{name}:")
        print(json.dumps(generate_schema(tool.fn), indent=2))
```

### Log Analysis

```python
# Setup logging completo per debug
import logging
from pathlib import Path

# Log file rotanti
from logging.handlers import RotatingFileHandler

# Setup logger principale
logger = logging.getLogger("mcp_server")
logger.setLevel(logging.DEBUG)

# File handler con rotazione
file_handler = RotatingFileHandler(
    "logs/mcp_server.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(
    logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter('%(levelname)s: %(message)s')
)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Usage in tools
@mcp.tool()
def logged_tool(data: str) -> str:
    logger.info(f"Tool execution started: {data[:50]}...")
    
    try:
        result = process_data(data)
        logger.info(f"Tool execution completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        raise
```

## 🎯 Conclusioni

L'integrazione MCP + OpenAI fornisce:

- **🚀 Potenza**: Capacità illimitate tramite tool personalizzati
- **🔧 Flessibilità**: Architettura modulare e scalabile  
- **🤝 Compatibilità**: Standard comune per tutti i client AI
- **🛡️ Sicurezza**: Controllo granulare delle operazioni

### Next Steps

1. **Implementa i tool base** seguendo gli esempi
2. **Testa con diversi client** (OpenAI, Claude, etc.)
3. **Aggiungi monitoring** e logging avanzato  
4. **Estendi con tool specifici** per il tuo use case
5. **Condividi tool riusabili** con la community

---

**Risorse Utili:**
- [Repository del Progetto](../README.md)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp) 
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

**Hai domande?** Consulta la sezione [Troubleshooting](#troubleshooting) o apri una issue nel repository.