## 🧠 MemU Chatbot Demo

This Streamlit app is an interactive AI-powered chatbot that demonstrates the capabilities of MemU, a future-oriented agentic memory system. It loads a sample conversation, memorizes it using MemU's hierarchical memory structure, and allows users to query the memory with natural language questions. The chatbot generates conversational responses based on retrieved memory context, and updates its memory with each new interaction.

### Features

- **MemU Integration**: Uses MemU for advanced memory management with hierarchical file system (Resource → Item → Category)
- **Dual Retrieval Methods**: Supports RAG (embedding-based) and LLM-based retrieval for semantic understanding
- **Interactive Chatbot**: Generates natural language responses using OpenRouter's GPT-4o model
- **Dynamic Memory Updates**: Memory grows with each conversation, allowing the chatbot to learn and remember
- **Streamlit UI**: User-friendly chat interface with message history

### MemU Features Used in This Prototype

MemU is an agentic memory framework that processes multimodal inputs and organizes them into a structured, hierarchical memory system. In this prototype app, we're leveraging the following key features:

1. **Hierarchical Memory Structure**:
   - **Resources**: Raw conversation data (JSON files)
   - **Items**: Extracted discrete memory units (preferences, habits, opinions, relationships)
   - **Categories**: Aggregated summaries (e.g., "preferences.md", "work_life.md")

2. **Memorization (`memorize()`)**:
   - Processes conversation files and extracts structured memory
   - Automatically categorizes and summarizes content
   - Builds a knowledge graph for efficient retrieval

3. **Retrieval (`retrieve()`)**:
   - **RAG-based**: Fast embedding vector search for speed
   - **LLM-based**: Deep semantic understanding with query rewriting
   - Progressive search: Categories → Items → Resources
   - Context-aware query processing

4. **Multimodal Support**: While this demo uses text conversations, MemU supports images, videos, audio, and documents

5. **Self-Evolving Memory**: The memory structure adapts based on usage patterns, improving over time

### Prerequisites

- Python 3.13+
- UV package manager
- OpenAI API key (for MemU operations)
- OpenRouter API key (for chatbot responses)
- Sample conversation file: `example/example_conversation.json`

### Setup with UV

1. **Install UV**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd llm_app_personalized_memory
   ```

3. **Create and activate Python 3.13 environment**:
   ```bash
   uv venv --python 3.13
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

### Environment Setup

Create a `.env` file in the project root with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Running the App

Start the MemU Chatbot Demo:

```bash
uv run streamlit run memu_chatbot.py
```

### Usage

1. **Load Memory**: Click "Load Memory Data" to initialize MemU with the sample conversation
2. **Chat**: Ask questions about the conversation in natural language
3. **Memory Growth**: Each interaction adds to the chatbot's memory, improving future responses

### Architecture

- **Frontend**: Streamlit for the chat interface
- **Memory Layer**: MemU for hierarchical memory management
- **LLM Layer**: OpenRouter for response generation
- **Persistence**: In-memory storage (can be upgraded to PostgreSQL with pgvector for persistence)

This prototype showcases how MemU can power intelligent, memory-aware AI applications with evolving knowledge bases.
