import os
import streamlit as st
from dotenv import load_dotenv
from memu.app import MemoryService
from openai import OpenAI
import asyncio
import tempfile
import json

st.title("MemU Chatbot Demo 🧠")
st.caption("Interactive chatbot demonstrating MemU memory retrieval from a sample conversation.")

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
file_path = os.path.abspath("example/example_conversation.json")

if not openai_api_key or not openrouter_api_key:
    st.error("OPENAI_API_KEY and OPENROUTER_API_KEY must be set in .env file.")
    st.stop()

if not os.path.exists(file_path):
    st.error(f"Example file not found: {file_path}. Please ensure 'example/example_conversation.json' exists.")
    st.stop()

# Initialize OpenRouter client
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_api_key)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory_loaded" not in st.session_state:
    st.session_state.memory_loaded = False
if "service" not in st.session_state:
    st.session_state.service = None
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

async def initialize_and_load_memory():
    """Initialize service and load memory - runs once."""
    service = MemoryService(
        llm_profiles={"default": {"api_key": openai_api_key}},
        database_config={"metadata_store": {"provider": "inmemory"}},
        retrieve_config={"method": "rag"},
    )
    memory = await service.memorize(resource_url=file_path, modality="conversation", user={"user_id": "123"})
    return service, memory

async def generate_response(service, prompt):
    """Retrieve memory and generate a response using LLM."""
    queries = [{"role": "user", "content": {"text": prompt}}]
    result = await service.retrieve(queries=queries, where={"user_id": "123"})
    
    # Build context from retrieved memory
    context = "Relevant past information:\n"
    for cat in result.get("categories", []):
        context += f"- {cat.get('summary', '')}\n"
    for item in result.get("items", []):
        context += f"- {item.get('summary', '')}\n"
    
    # Prepare the full prompt
    full_prompt = f"{context}\nHuman: {prompt}\nAI:"
    
    # Generate response using OpenRouter
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant with access to past conversations."},
            {"role": "user", "content": full_prompt}
        ]
    )
    return response.choices[0].message.content

async def main():
    """Main async function that handles all MemU operations."""
    # Load memory if not already loaded
    if not st.session_state.memory_loaded:
        if st.button("Load Memory Data"):
            with st.spinner("Loading and memorizing conversation data..."):
                service, memory = await initialize_and_load_memory()
                st.session_state.service = service
                st.session_state.memory_loaded = True
                st.success("Memory loaded successfully!")
                if memory.get("categories"):
                    st.write("**Loaded Categories:**")
                    for cat in memory.get("categories", []):
                        st.write(f"- {cat.get('name')}: {cat.get('summary', '')}")
                st.rerun()
        return

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about the conversation..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Generating response..."):
            response = await generate_response(st.session_state.service, prompt)

        # Add the conversation to memory
        conversation = {
            "messages": [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response}
            ]
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(conversation, f)
            temp_file = f.name
        try:
            await st.session_state.service.memorize(resource_url=temp_file, modality="conversation", user={"user_id": "123"})
        finally:
            os.unlink(temp_file)

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

# Run the async main function
asyncio.run(main())
