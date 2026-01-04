## 🧠 LLM Apps with Personalized Memory

This repository contains two Streamlit applications demonstrating advanced AI memory capabilities using MemU.

---

## 📱 Applications

### 1. MemU Chatbot Demo (`memu_chatbot.py`)
An interactive text-based chatbot with hierarchical memory management.

### 2. Anam AI Avatar Agent (`anam_avatar_agent.py`)
A real-time AI avatar with video/audio streaming and persistent memory.

---

## 🎭 Anam AI Avatar Agent

This application creates an interactive AI avatar using **Anam AI** for realistic video personas and **MemU** for persistent memory storage.

### Features

- **Real-time Video Avatar**: Photorealistic AI persona with natural facial expressions and lip-sync
- **Voice Interaction**: Speak directly to your avatar using your microphone
- **MemU Memory Integration**: Conversations are stored and retrieved for personalized responses
- **Customizable Persona**: Choose avatar appearance, voice, and personality
- **Multi-language Support**: 50+ languages and accents available

### Anam AI Features Used

1. **Session Token Authentication**: Secure API access via session tokens
2. **WebRTC Streaming**: Real-time video/audio streaming to browser
3. **Persona Configuration**:
   - `avatarId`: Visual appearance of the avatar
   - `voiceId`: Voice characteristics
   - `llmId`: Language model for responses
   - `systemPrompt`: Personality and behavior instructions
4. **Event Handling**: User and agent transcript events for conversation logging
5. **Connection State Management**: Real-time status updates

### Running the Avatar Agent

```bash
uv run streamlit run anam_avatar_agent.py
```

---

## 🧠 MemU Chatbot Demo

This Streamlit app is an interactive AI-powered chatbot that demonstrates the capabilities of MemU, a future-oriented agentic memory system. It loads a sample conversation, memorizes it using MemU's hierarchical memory structure, and allows users to query the memory with natural language questions.

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

2. **Memorization (`memorize()` / `memorize_conversation()`)**:
   - Processes conversation files and extracts structured memory
   - Automatically categorizes and summarizes content
   - Builds a knowledge graph for efficient retrieval

3. **Retrieval (`retrieve()` / `search()`)**:
   - **RAG-based**: Fast embedding vector search for speed
   - **LLM-based**: Deep semantic understanding with query rewriting
   - Progressive search: Categories → Items → Resources
   - Context-aware query processing

4. **Multimodal Support**: While this demo uses text conversations, MemU supports images, videos, audio, and documents

5. **Self-Evolving Memory**: The memory structure adapts based on usage patterns, improving over time

### Running the Chatbot

```bash
uv run streamlit run memu_chatbot.py
```

---

## 🚀 Setup with UV

### Prerequisites

- Python 3.13+
- UV package manager
- API Keys (see Environment Setup)

### 1. Install UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd llm_app_personalized_memory
```

### 3. Create Python 3.13 Environment

```bash
uv venv --python 3.13
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 4. Install Dependencies

```bash
uv pip install -r requirements.txt
```

---

## 🔑 Environment Setup

Create a `.env` file in the project root with your API keys:

```env
# For MemU memory operations
MEMU_API_KEY=your_memu_api_key_here

# For OpenRouter LLM (Chatbot)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# For Anam AI Avatar
ANAM_API_KEY=your_anam_api_key_here

# For MemU internal operations (if needed)
OPENAI_API_KEY=your_openai_api_key_here
```

### Getting API Keys

| Service | URL |
|---------|-----|
| MemU | [memu.ai](https://memu.ai) |
| OpenRouter | [openrouter.ai](https://openrouter.ai) |
| Anam AI | [lab.anam.ai/register](https://lab.anam.ai/register) |
| OpenAI | [platform.openai.com](https://platform.openai.com) |

---

## 🏃 Running the Apps

### MemU Chatbot (Text-based)

```bash
uv run streamlit run memu_chatbot.py
```

### Anam AI Avatar Agent (Video/Audio)

```bash
uv run streamlit run anam_avatar_agent.py
```

---

## 🏗️ Architecture

### MemU Chatbot
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Streamlit  │────▶│    MemU     │────▶│  OpenRouter │
│     UI      │◀────│   Memory    │◀────│     LLM     │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Anam AI Avatar Agent
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Streamlit  │────▶│   Anam AI   │────▶│    MemU     │
│     UI      │◀────│   Avatar    │◀────│   Memory    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       │    WebRTC Stream  │
       └───────────────────┘
```

---

## 📁 Project Structure

```
llm_app_personalized_memory/
├── memu_chatbot.py        # Text-based chatbot with MemU
├── anam_avatar_agent.py   # AI Avatar with Anam + MemU
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this file)
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

---

## 🎯 Usage Tips

### For the Chatbot
1. Start the app and wait for MemU to initialize
2. Type your message in the chat input
3. The bot will retrieve relevant memories and respond
4. Each conversation is automatically saved to memory

### For the Avatar Agent
1. Configure your avatar in the sidebar
2. Click "Start Avatar Session"
3. Allow microphone access when prompted
4. Speak naturally to interact with your avatar
5. Click "Save Conversation to Memory" to persist the conversation

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Check your `.env` file has all required keys |
| Avatar won't load | Ensure ANAM_API_KEY is valid and you have internet |
| Memory errors | Verify MEMU_API_KEY is correct |
| No audio | Check browser microphone permissions |

---

## 📚 Resources

- [MemU Documentation](https://github.com/memu-ai/memu)
- [Anam AI Documentation](https://docs.anam.ai)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Streamlit Documentation](https://docs.streamlit.io)

---

This prototype showcases how MemU can power intelligent, memory-aware AI applications with evolving knowledge bases, combined with cutting-edge avatar technology from Anam AI.
