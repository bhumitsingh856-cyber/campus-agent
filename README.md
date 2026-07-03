# Campus Bot

An intelligent conversational AI assistant for campus student services, powered by LangGraph and deployed across Telegram and WhatsApp platforms.

## Overview

Campus Bot is a multi-channel AI agent that provides students with instant access to academic information, attendance records, and general campus support. The bot uses agentic AI workflows with LLM tool-calling capabilities, state management via PostgreSQL checkpointer, and vector-based retrieval for intelligent responses.

**Supported Channels:**
- Telegram
- WhatsApp
- HTTP REST API

## Features

### Core Capabilities

- **Attendance Retrieval**: Fetch real-time student attendance via institutional portal integration
- **Syllabus Access**: Retrieve official scheme and syllabus for engineering branches (CSE, CSE-AIML, CSE-DS, CS-IT)
- **Student Profile Management**: Register/unregister and retrieve student details
- **Web Search & Scraping**: Real-time information gathering using Tavily Search and Firecrawl
- **Vector-based Retrieval**: Semantic search over institutional documents via Pinecone
- **Conversation History**: Persistent session management with PostgreSQL-backed checkpointing

### User Commands

```
/start          - Display welcome message and available commands
/register       - Register student account (format: /register <computer-code> <password>)
/unregister     - Unregister student account
/profile        - View registered student details
/clear          - Clear conversation history
/help           - Display all available commands
```

## Architecture

```
Campus Bot
├── FastAPI Application (main.py)
│   ├── Lifespan Management (DB & Workflow Initialization)
│   └── Routes
│       ├── /telegram       - Telegram webhook endpoint
│       ├── /whatsapp-webhook - WhatsApp webhook endpoint
│       ├── /bot            - REST API endpoint
│       └── /              - Health check
│
├── Agent Layer (src/agent/)
│   ├── workflow.py        - LangGraph state machine with tool nodes
│   ├── llm.py            - LLM configuration (Cerebras GLM-4.7)
│   ├── tools/tools.py    - Tool definitions for agent actions
│   └── prompt/sys.py     - System prompts
│
├── Data Layer (src/db/)
│   ├── checkpointer.py   - PostgreSQL checkpoint storage
│   └── vector.py         - Pinecone vector retriever
│
├── Integration Layer (src/routes/)
│   ├── telegram.py       - Telegram bot handler
│   ├── whatsapp.py       - WhatsApp webhook handler
│   └── bot.py            - REST API handler
│
└── Utilities (src/utils/)
    ├── command_handler.py  - Command parsing and routing
    ├── register_user.py    - Student registration logic
    ├── clear_history.py    - Session history management
    └── start_message.py    - Welcome messages
```

## Technology Stack

### Core Framework
- **FastAPI** - Web framework for API endpoints
- **LangGraph** - Agentic AI workflow orchestration
- **LangChain** - LLM abstractions and tool calling

### LLM & AI
- **Cerebras GLM-4.7** - Primary language model
- **LangChain-Groq** - Optional LLM provider
- **LangChain-Google** - Optional Gemini integration
- **TavilySearch** - Web search and extraction

### Data & Storage
- **PostgreSQL** - Session checkpoints and vector store with psycopg async pool
- **Pinecone** - Vector embeddings for semantic search
- **Firecrawl** - Web scraping and page interaction

### Messaging Platforms
- **Telegram Bot API** - Telegram integration
- **Twilio** - WhatsApp integration

### Utilities
- **Pydantic** - Data validation
- **python-dotenv** - Environment configuration
- **pypdf** - PDF processing

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- API Keys for:
  - Cerebras (LLM)
  - Telegram Bot Token
  - Twilio (WhatsApp)
  - Firecrawl API
  - Tavily Search
  - Pinecone

### Setup

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd Campus\ Bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Required variables:
   ```env
    GROQ_API_KEY=your_key
    CEREBRAS_API_KEY=your_key
    NVIDIA_API_KEY=your_key
    CEREBRAS_LLM=your_model_name

    TAVILY_API_KEY=your_key 
    FIRECRAWL_API_KEY=your_key 

    PINECONE_API_KEY=your_key
    PINECONE_INDEX_NAME=your_index

    PGSQL_URL=your_neon_db_url 

    TELEGRAM_ACCESS_TOKEN=your_token
    TELEGRAM_WEBHOOK_URL=your_webhook_url/telegram

    LANGSMITH_TRACING=boolean
    LANGSMITH_ENDPOINT=your_endpoint
    LANGSMITH_API_KEY=your_key
    LANGSMITH_PROJECT=your_project_name

   # Optional LLMs
   GROQ_API_KEY=optional 
   ```

5. **Initialize database**
   ```bash
   # The database schema is created automatically on app startup
   # Ensure PostgreSQL is running and accessible
   ```

## Running the Application

### Development Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Health Check
```bash
curl http://localhost:8000/
```

Response:
```json
{"success": true}
```

## API Endpoints

### REST Endpoint
**POST** `/bot`

Query a student with the bot.

```bash
curl -X POST "http://localhost:8000/bot?req=What%20is%20my%20attendance&thread_id=student123"
```

**Parameters:**
- `req` (string): User query
- `thread_id` (string): Unique student/session identifier

**Response:**
```json
"content": "Your current attendance is 85%..."
```

### Telegram
Webhook URL: `POST /telegram`
- Configured via environment variable `TELEGRAM_WEBHOOK_URL`
- Messages received via Telegram will be processed as user queries

### WhatsApp
Webhook URL: `POST /whatsapp-webhook`
- Integrated with Twilio
- Messages received via WhatsApp will be processed as user queries

## Workflow & State Management

### LangGraph State Machine

```
START
  ↓
[chat node]
  ↓ (conditional tools_condition)
  ├─→ No tools needed → END
  └─→ Tools required → [tools node]
        ↓
      [chat node] (resume with tool results)
        ↓
       END
```

### Session Management

Each user has a persistent conversation thread identified by `thread_id`. The system maintains:
- Message history with context windowing (7000 tokens max)
- Tool call results and responses
- Student profile information via vector store

All state is checkpointed to PostgreSQL for recovery and audit trails.

## Tool Definitions

### `get_attendance(computer_code, password)`
Retrieves student attendance records by scraping the institutional portal.

### `get_syllabus(course)`
Returns syllabus and scheme details for engineering branches.
- Supported: `CSE`, `CSE-AIML`, `CSE-DS`, `CS-IT`

### `web_search(query)`
Performs web search for real-time information.

### `semantic_search(query)`
Retrieves relevant documents from the vector knowledge base.

## Configuration

### LLM Model Selection

The current model is **Cerebras GLM-4.7**. To switch models, edit `src/agent/llm.py`:

```python
# Option 1: Cerebras (Current)
llm = ChatCerebras(model="zai-glm-4.7")

# Option 2: Groq
llm = ChatGroq(model="openai/gpt-oss-120b")

```

### Context Window Management

Adjust message trimming in `src/agent/workflow.py`:
```python
msg = trim_messages(
    messages=state['messages'],
    token_counter=count_tokens_approximately,
    max_tokens=7000,  # ← Change this value
    strategy="last"
)
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `psql <PGSQL_URL>`
- Check connection pool settings in `src/db/checkpointer.py`
- Ensure `PGSQL_URL` is correctly formatted

### Workflow Not Initializing
- The workflow is compiled lazily after `init_db()` completes
- If checkpointer is `None`, the app will raise a `RuntimeError`
- Check app logs for initialization order errors

### Tool Failures
- **Web scraping**: Verify Firecrawl API key and target URLs are accessible
- **Vector search**: Ensure Pinecone index is populated with documents
- **Portal access**: Student credentials must be valid for institutional portal

### Message Delivery Issues
- **Telegram**: Verify webhook URL is publicly accessible
- **WhatsApp**: Ensure Twilio credentials and phone number are configured

## Development

### Project Structure
```
src/
├── agent/          - LangGraph workflow and LLM setup
├── db/             - Data persistence and vector retrieval
├── routes/         - Platform integrations
└── utils/          - Helper functions
```

### Adding New Tools

1. Define the tool function in `src/agent/tools/tools.py`:
   ```python
   @tool
   async def my_tool(param: str):
       """Tool description for LLM."""
       return result
   ```

2. Add to tools list in `src/agent/workflow.py`:
   ```python
   from src.agent.tools.tools import tools, my_tool
   tools = [*tools, my_tool]
   ```

3. The LLM will automatically discover and invoke the tool.

### Adding New Commands

1. Add handler in `src/utils/command_handler.py`:
   ```python
   if lower == "/mycommand":
       return {"handled": True, "message": "Response"}
   ```

## Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment-Specific Deployment
- Development: `uvicorn main:app --reload`
- Staging: `uvicorn main:app --workers 2`
- Production: `uvicorn main:app --workers 4 --log-config logging.yaml`

## Monitoring & Logging

Enable verbose logging by setting environment variable:
```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your_key
```

View logs:
```bash
tail -f application.log
```

## License

Proprietary - IPS Academy Campus Project

## Support

For issues or feature requests, contact the development team.
