# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Copy environment template and configure
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY
```

### Running the Application
The application requires three separate services to run concurrently:

#### Option 1: Original MCP Server (FastAPI only)
```bash
# Terminal 1: Start MCP Server (port 8001)
uv run python scripts/run_mcp_server.py

# Terminal 2: Start Backend API (port 8000) 
uv run python scripts/run_backend.py

# Terminal 3: Start Frontend UI (port 8501)
uv run python scripts/run_frontend.py
```

#### Option 2: FastMCP Hybrid Server (recommended)
```bash
# Terminal 1: Start Hybrid MCP Server (port 8001) - supports both FastMCP and REST API
uv run python scripts/run_hybrid_mcp.py

# Terminal 2: Start Backend API (port 8000) 
uv run python scripts/run_backend.py

# Terminal 3: Start Frontend UI (port 8501)
uv run python scripts/run_frontend.py
```

#### Option 3: Pure FastMCP Server (for Claude integration only)
```bash
# For Claude Desktop integration (stdio transport)
uv run python scripts/run_fastmcp_server.py

# For HTTP integration (not compatible with current backend)
uv run python scripts/run_fastmcp_http.py
```

### Development Tools
```bash
# Code formatting
uv run black src/

# Linting
uv run ruff check src/

# Type checking
uv run mypy src/

# Run tests
uv run pytest
```

## Architecture Overview

This is a multi-service chatbot application that integrates OpenAI with MCP (Model Context Protocol) tools:

### Core Components

1. **Backend (`src/backend/`)**
   - FastAPI server that orchestrates chat interactions
   - Manages conversations in-memory via `ConversationManager`
   - Integrates OpenAI client with MCP tools through `MCPClient`
   - Main entry point: `main.py` with `/chat` endpoint

2. **MCP Server (`src/mcp_server/`)**
   - Standalone FastAPI server providing tool execution capabilities
   - `ToolRegistry` manages available tools (time, calculator, weather, etc.)
   - Converts tool schemas to OpenAI function calling format
   - Tools are defined in `tools.py` and registered automatically

3. **Frontend (`src/frontend/`)**
   - Streamlit web interface for chat interactions
   - Real-time status monitoring of backend services
   - Conversation history and tool usage display

### Data Flow
1. User sends message via Streamlit frontend
2. Frontend calls `/chat` endpoint on backend
3. Backend adds message to conversation via `ConversationManager`
4. If tools enabled, backend fetches available tools from MCP server
5. Backend sends conversation to OpenAI with tool definitions
6. If OpenAI requests tool execution, backend calls MCP server
7. Backend processes tool results and generates final response
8. Response returned through frontend with tool usage indicators

### Key Design Patterns
- **Pydantic models** for data validation across all services
- **Async/await** for non-blocking HTTP requests
- **FastAPI dependency injection** for configuration management
- **In-memory storage** for conversations (no persistence layer)
- **CORS enabled** for cross-origin requests between services

### Configuration
Environment variables are managed through `pydantic-settings`:
- OpenAI API configuration (key, model, temperature)
- Service host/port settings for backend and MCP server
- Configuration loaded via `.env` file

### MCP Tool System
Tools are defined with JSON Schema parameters and automatically converted to OpenAI function format. Adding new tools requires:
1. Define tool schema in `ToolRegistry._register_default_tools()`
2. Implement handler method in `ToolRegistry`
3. Tools are automatically discovered and exposed via `/tools` endpoint