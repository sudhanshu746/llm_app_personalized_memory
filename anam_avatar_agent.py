"""
🎭 Anam AI Avatar Agent with MemU Memory

This Streamlit application creates an interactive AI avatar using Anam AI
for realistic video personas and MemU for persistent memory storage.

Features:
- Real-time AI avatar with video/audio streaming (Anam AI)
- Persistent conversation memory (MemU)
- Memory-aware responses that learn from past interactions
- Beautiful Streamlit UI with embedded avatar
"""

import streamlit as st
import os
import requests
import asyncio
import tempfile
import json
from dotenv import load_dotenv
from memu.app import MemoryService

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Anam AI Avatar with MemU Memory",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .avatar-container {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        background: #1a1a2e;
    }
    .memory-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .status-connected {
        color: #00ff88;
        font-weight: bold;
    }
    .status-disconnected {
        color: #ff4757;
        font-weight: bold;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background: #e3f2fd;
        text-align: right;
    }
    .assistant-message {
        background: #f5f5f5;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "avatar_active" not in st.session_state:
    st.session_state.avatar_active = False
if "total_conversations" not in st.session_state:
    st.session_state.total_conversations = 0
if "memory_items" not in st.session_state:
    st.session_state.memory_items = 0
if "memu_service" not in st.session_state:
    st.session_state.memu_service = None
if "memory_initialized" not in st.session_state:
    st.session_state.memory_initialized = False


async def initialize_memu_service():
    """Initialize MemU memory service for memory storage."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("❌ OPENAI_API_KEY not found in environment variables.")
        st.info("Please add OPENAI_API_KEY to your .env file for MemU memory")
        return None
    
    service = MemoryService(
        llm_profiles={"default": {"api_key": openai_api_key}},
        database_config={"metadata_store": {"provider": "inmemory"}},
        retrieve_config={"method": "rag"},
    )
    return service


def get_anam_session_token(persona_config: dict) -> str:
    """
    Create a session token for Anam AI avatar.
    
    Args:
        persona_config: Configuration for the AI persona
        
    Returns:
        Session token string
    """
    api_key = os.getenv("ANAM_API_KEY")
    if not api_key:
        st.error("❌ ANAM_API_KEY not found in environment variables.")
        return None
    
    try:
        response = requests.post(
            "https://api.anam.ai/v1/auth/session-token",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={"personaConfig": persona_config}
        )
        response.raise_for_status()
        return response.json().get("sessionToken")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to get Anam session token: {e}")
        return None


async def save_conversation_to_memory(memu_service: MemoryService, messages: list):
    """
    Save conversation history to MemU memory.
    
    Args:
        memu_service: MemU service instance
        messages: List of conversation messages
    
    Returns:
        True if successful, False otherwise
    """
    if not messages or len(messages) < 2:
        return False
    
    try:
        conversation = {"messages": []}
        for msg in messages:
            conversation["messages"].append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(conversation, f)
            temp_file = f.name
        
        try:
            await memu_service.memorize(
                resource_url=temp_file,
                modality="conversation",
                user={"user_id": "avatar_user"}
            )
        finally:
            os.unlink(temp_file)
        
        return True
    except Exception as e:
        st.error(f"❌ Failed to save to memory: {e}")
        return False


async def get_memory_context(memu_service: MemoryService, query: str) -> str:
    """
    Retrieve relevant memory context for a query.
    
    Args:
        memu_service: MemU service instance
        query: User's query
        
    Returns:
        Memory context string
    """
    try:
        queries = [{"role": "user", "content": {"text": query}}]
        result = await memu_service.retrieve(queries=queries, where={"user_id": "avatar_user"})
        
        context_parts = []
        for cat in result.get("categories", []):
            summary = cat.get("summary", "")
            if summary:
                context_parts.append(f"- {summary}")
        for item in result.get("items", []):
            summary = item.get("summary", "")
            if summary:
                context_parts.append(f"- {summary}")
        
        return "\n".join(context_parts) if context_parts else ""
    except Exception as e:
        st.warning(f"⚠️ Could not retrieve memory: {e}")
        return ""


def build_system_prompt_with_memory(base_prompt: str, memory_context: str) -> str:
    """
    Build a system prompt that includes memory context.
    
    Args:
        base_prompt: Base system prompt
        memory_context: Retrieved memory context
        
    Returns:
        Enhanced system prompt
    """
    if memory_context:
        return f"""{base_prompt}

You have the following relevant memories from previous conversations:
<memory>
{memory_context}
</memory>

Use these memories to provide personalized, context-aware responses. Reference past conversations naturally when relevant."""
    return base_prompt


def render_avatar_component(session_token: str):
    """
    Render the Anam AI avatar using embedded HTML/JS.
    
    Args:
        session_token: Anam session token
    """
    avatar_html = f"""
    <div id="avatar-wrapper" style="width: 100%; max-width: 640px; margin: 0 auto;">
        <video 
            id="persona-video" 
            autoplay 
            playsinline 
            style="width: 100%; border-radius: 16px; background: #1a1a2e;"
        ></video>
        <div id="status" style="text-align: center; padding: 10px; font-size: 14px; color: #666;">
            Connecting to avatar...
        </div>
        <div id="transcript" style="
            max-height: 200px; 
            overflow-y: auto; 
            padding: 10px; 
            background: #f8f9fa; 
            border-radius: 8px; 
            margin-top: 10px;
            font-size: 14px;
        ">
            <p style="color: #999; text-align: center;">Conversation transcript will appear here...</p>
        </div>
    </div>
    
    <script type="module">
        import {{ createClient, AnamEvent }} from "https://esm.sh/@anam-ai/js-sdk@latest";
        
        const sessionToken = "{session_token}";
        const statusElement = document.getElementById("status");
        const transcriptElement = document.getElementById("transcript");
        
        let conversationLog = [];
        
        function addToTranscript(role, text) {{
            const msgDiv = document.createElement("div");
            msgDiv.style.padding = "8px";
            msgDiv.style.marginBottom = "8px";
            msgDiv.style.borderRadius = "8px";
            
            if (role === "user") {{
                msgDiv.style.background = "#e3f2fd";
                msgDiv.style.textAlign = "right";
                msgDiv.innerHTML = "<strong>You:</strong> " + text;
            }} else {{
                msgDiv.style.background = "#f5f5f5";
                msgDiv.style.textAlign = "left";
                msgDiv.innerHTML = "<strong>Avatar:</strong> " + text;
            }}
            
            // Clear placeholder if first message
            if (conversationLog.length === 0) {{
                transcriptElement.innerHTML = "";
            }}
            
            transcriptElement.appendChild(msgDiv);
            transcriptElement.scrollTop = transcriptElement.scrollHeight;
            
            conversationLog.push({{ role: role, content: text, timestamp: new Date().toISOString() }});
            
            // Store in localStorage for Python to access
            localStorage.setItem("anam_conversation", JSON.stringify(conversationLog));
        }}
        
        async function startAvatar() {{
            try {{
                statusElement.textContent = "Initializing avatar...";
                statusElement.style.color = "#ffa726";
                
                const anamClient = createClient(sessionToken);
                
                // Set up event listeners using addListener and AnamEvent enum
                anamClient.addListener(AnamEvent.CONNECTION_ESTABLISHED, () => {{
                    statusElement.textContent = "✅ Connected! Start speaking...";
                    statusElement.style.color = "#00c853";
                }});
                
                anamClient.addListener(AnamEvent.CONNECTION_CLOSED, () => {{
                    statusElement.textContent = "❌ Disconnected";
                    statusElement.style.color = "#ff5252";
                }});
                
                anamClient.addListener(AnamEvent.VIDEO_PLAY_STARTED, () => {{
                    console.log("Video stream started");
                }});
                
                // Listen for conversation updates (complete history)
                anamClient.addListener(AnamEvent.MESSAGE_HISTORY_UPDATED, (messages) => {{
                    console.log("Conversation updated:", messages);
                    // Update transcript with full history
                    transcriptElement.innerHTML = "";
                    conversationLog = [];
                    messages.forEach((msg) => {{
                        addToTranscript(msg.role === "assistant" ? "assistant" : "user", msg.content);
                    }});
                }});
                
                // Listen for real-time transcription
                anamClient.addListener(AnamEvent.MESSAGE_STREAM_EVENT_RECEIVED, (event) => {{
                    if (event.type === "persona") {{
                        // Persona speaking - could show real-time updates
                        console.log("Persona speaking:", event.text);
                    }} else if (event.type === "user") {{
                        // User finished speaking
                        console.log("User said:", event.text);
                    }}
                }});
                
                // Start streaming to video element
                await anamClient.streamToVideoElement("persona-video");
                
                statusElement.textContent = "✅ Connected! Start speaking...";
                statusElement.style.color = "#00c853";
                
            }} catch (error) {{
                console.error("Failed to start avatar:", error);
                statusElement.textContent = "❌ Failed to connect: " + error.message;
                statusElement.style.color = "#ff5252";
            }}
        }}
        
        // Auto-start when loaded
        startAvatar();
    </script>
    """
    
    st.components.v1.html(avatar_html, height=600, scrolling=True)


async def main():
    """Main async application entry point."""
    
    # Header
    st.markdown('<h1 class="main-header">🎭 AI Avatar with MemU Memory and Anam</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; color: #666; font-size: 1.1rem;">
        Interactive AI Avatar powered by Anam AI with persistent memory via MemU
    </p>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Avatar Configuration")
        
        # Avatar selection
        avatar_options = {
            "Cara (Default)": "30fa96d0-26c4-4e55-94a0-517025942e18",
            "Richard": "richard-avatar-id",
            "Ben": "ben-avatar-id",
            "Liv": "liv-avatar-id",
            "Custom": "custom"
        }
        selected_avatar = st.selectbox("Select Avatar", list(avatar_options.keys()))
        
        # Voice selection
        voice_options = {
            "Default Voice": "6bfbe25a-979d-40f3-a92b-5394170af54b",
            "Custom": "custom"
        }
        selected_voice = st.selectbox("Select Voice", list(voice_options.keys()))
        
        # Persona name
        persona_name = st.text_input("Persona Name", value="Maya")
        
        # System prompt
        default_prompt = """You are Maya, a friendly and helpful AI doctor’s assistant. Your role is to check the user's current medications, ask proactively about the last medications they've taken (using memory or prior user history if available), and provide assistance or reminders as needed.

- Always respond in a warm, conversational manner appropriate for a healthcare assistant.
- Use empathetic language and active listening techniques to build rapport with the user.
- Be concise and clear in your communication.
- When interacting with a user, first recall and mention any medications mentioned or logged previously (if such data exists).
- Proactively ask the user about their last medications: inquire about times taken, missed doses, changes, or any side effects.
- Offer to help log new medications, remind about dosage or schedules, and answer related questions.
- Do not give direct clinical advice or prescription suggestions—instead, guide the user to consult a healthcare professional for such needs.
- If no memory or medication history is present, gently prompt the user to share their current medications.
- If the user mentions changes in medication or new symptoms, ask for clarifying details and offer supportive suggestions (e.g., tracking, discussing with their doctor, etc.).

**Output Format:**  
Always respond in concise, friendly conversational English, suitable for a chat interface. Limit replies to 2-4 short paragraphs.

**Examples:**

**Example 1:**  
_User’s medication memory_: “Last logged: Lisinopril 10mg at 8am.”  
Maya: “Welcome back Sudhanshu! I see you last took Lisinopril 10mg at 8am. Have you taken your next dose yet, or are there any changes to your medication plan? If you’ve experienced any side effects, let me know so I can help keep track for you!”

**Example 2:**  
_(No medication memory found)_  
Maya: “Hi Sudhanshu! I don’t have any medications logged for you yet. Can you tell me what medications you’re currently taking? I can help you track your schedule and remind you if you’d like.”

**Example 3:**  
_User: “I missed my last dose of metformin.”_  
Maya: “Thank you for letting me know you missed your last dose of metformin. Would you like me to remind you about your next dose, or help you log your medication times more regularly? Always let your doctor know about any missed doses, especially if you feel unwell.”

**Important Reminder:**  
You are a proactive and friendly AI doctor assistant. Always check or recall the user’s medication history if available, ask about current or recent medication use, and offer appropriate, non-clinical assistance. Never give medical advice—prompt users to contact their healthcare provider for medical concerns."""
        
        system_prompt = st.text_area(
            "System Prompt",
            value=default_prompt,
            height=150
        )
        
        st.divider()
        
        # Memory controls
        st.header("🧠 Memory Settings")
        enable_memory = st.checkbox("Enable MemU Memory", value=True)
        
        if enable_memory:
            if st.button("🗑️ Clear Memory"):
                if "conversation_history" in st.session_state:
                    st.session_state.conversation_history = []
                st.session_state.memory_initialized = False
                st.session_state.memu_service = None
                st.success("Memory cleared!")
        
        st.divider()
        
        # API Key status
        st.header("🔑 API Status")
        anam_key = os.getenv("ANAM_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        st.write("ANAM_API_KEY:", "✅ Set" if anam_key else "❌ Missing")
        st.write("OPENAI_API_KEY:", "✅ Set" if openai_key else "❌ Missing")
    
    # Initialize MemU service if memory is enabled and not yet initialized
    if enable_memory and not st.session_state.memory_initialized:
        if st.button("🧠 Initialize Memory Service"):
            with st.spinner("Initializing MemU memory service..."):
                service = await initialize_memu_service()
                if service:
                    st.session_state.memu_service = service
                    st.session_state.memory_initialized = True
                    st.success("✅ Memory service initialized!")
                    st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎬 AI Avatar")
        
        # Check for API keys
        if not os.getenv("ANAM_API_KEY"):
            st.error("""
            ❌ **ANAM_API_KEY not found!**
            
            Please add your Anam AI API key to the `.env` file:
            ```
            ANAM_API_KEY=your_anam_api_key_here
            ```
            
            Get your API key at: https://lab.anam.ai/register
            """)
        else:
            # Initialize avatar session
            if st.button("🚀 Start Avatar Session", type="primary", use_container_width=True):
                with st.spinner("Initializing avatar..."):
                    # Get memory context if enabled
                    memory_context = ""
                    if enable_memory and st.session_state.memu_service:
                        memory_context = await get_memory_context(
                            st.session_state.memu_service, 
                            "general conversation context"
                        )
                    
                    # Build enhanced system prompt
                    enhanced_prompt = build_system_prompt_with_memory(
                        system_prompt, 
                        memory_context
                    )
                    
                    # Configure persona
                    persona_config = {
                        "name": persona_name,
                        "avatarId": avatar_options.get(selected_avatar, avatar_options["Cara (Default)"]),
                        "voiceId": voice_options.get(selected_voice, voice_options["Default Voice"]),
                        "llmId": "0934d97d-0c3a-4f33-91b0-5e136a0ef466",
                        "systemPrompt": enhanced_prompt,
                        "maxSessionLengthSeconds": 600
                    }
                    
                    # Get session token
                    session_token = get_anam_session_token(persona_config)
                    
                    if session_token:
                        st.session_state.avatar_active = True
                        st.session_state.session_token = session_token
                        st.success("✅ Avatar session started!")
            
            # Render avatar if active
            if st.session_state.get("avatar_active") and st.session_state.get("session_token"):
                render_avatar_component(st.session_state.session_token)
                
                # Save conversation button
                if enable_memory and st.session_state.memu_service:
                    if st.button("💾 Save Conversation to Memory"):
                        if "conversation_history" in st.session_state and st.session_state.conversation_history:
                            success = await save_conversation_to_memory(
                                st.session_state.memu_service, 
                                st.session_state.conversation_history
                            )
                            if success:
                                st.success("✅ Conversation saved to MemU memory!")
                        else:
                            st.warning("No conversation to save yet.")
    
    with col2:
        st.subheader("🧠 Memory Status")
        
        if enable_memory:
            if st.session_state.memory_initialized and st.session_state.memu_service:
                st.info("""
                **MemU Memory Active**
                
                Your conversations are being stored and will be used 
                to provide personalized responses in future sessions.
                """)
                
                # Memory stats (placeholder - actual implementation depends on MemU API)
                with st.expander("📊 Memory Statistics"):
                    st.metric("Total Conversations", st.session_state.get("total_conversations", 0))
                    st.metric("Memory Items", st.session_state.get("memory_items", 0))
                
                # Recent memories
                with st.expander("📝 Recent Memories"):
                    if "conversation_history" in st.session_state and st.session_state.conversation_history:
                        for msg in st.session_state.conversation_history[-5:]:
                            role_icon = "👤" if msg["role"] == "user" else "🤖"
                            st.write(f"{role_icon} {msg['content'][:100]}...")
                    else:
                        st.write("No recent memories yet.")
            else:
                st.warning("Memory service not initialized. Click 'Initialize Memory Service' above.")
        else:
            st.warning("Memory is disabled. Enable it in the sidebar to store conversations.")
        
        st.divider()
        
        # Instructions
        st.subheader("📖 How to Use")
        st.markdown("""
        1. **Initialize** memory service (if enabled)
        2. **Configure** your avatar in the sidebar
        3. **Start** the avatar session
        4. **Speak** to interact with your AI avatar
        5. **Save** conversations to build memory
        
        The avatar will remember past conversations
        and provide personalized responses!
        """)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #999; font-size: 0.9rem;">
        Powered by <a href="https://anam.ai" target="_blank">Anam AI</a> for avatars 
        and <a href="https://github.com/memu-ai/memu" target="_blank">MemU</a> for memory
    </div>
    """, unsafe_allow_html=True)


# Run the async main function
asyncio.run(main())
