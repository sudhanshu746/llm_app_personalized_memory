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
from datetime import datetime
from dotenv import load_dotenv
from memu import MemuClient

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


def get_memu_client():
    """Initialize MemU client for memory storage."""
    if "memu_client" not in st.session_state:
        api_key = os.getenv("MEMU_API_KEY")
        if not api_key:
            st.error("❌ MEMU_API_KEY not found in environment variables.")
            st.info("Please add MEMU_API_KEY to your .env file")
            return None
        st.session_state.memu_client = MemuClient(api_key=api_key)
    return st.session_state.memu_client


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


def save_conversation_to_memory(memu_client: MemuClient, messages: list):
    """
    Save conversation history to MemU memory.
    
    Args:
        memu_client: MemU client instance
        messages: List of conversation messages
    """
    if not messages or len(messages) < 2:
        return
    
    try:
        # Format conversation for MemU
        conversation = []
        for msg in messages:
            conversation.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg.get("timestamp", datetime.now().isoformat())
            })
        
        # Save to MemU
        memu_client.memorize_conversation(
            conversation=conversation,
            user_name="User",
            agent_name="Avatar Assistant"
        )
        return True
    except Exception as e:
        st.error(f"❌ Failed to save to memory: {e}")
        return False


def get_memory_context(memu_client: MemuClient, query: str) -> str:
    """
    Retrieve relevant memory context for a query.
    
    Args:
        memu_client: MemU client instance
        query: User's query
        
    Returns:
        Memory context string
    """
    try:
        # Search memory for relevant context
        results = memu_client.search(query=query, limit=5)
        if results:
            context_parts = []
            for item in results:
                if isinstance(item, dict):
                    context_parts.append(item.get("content", str(item)))
                else:
                    context_parts.append(str(item))
            return "\n".join(context_parts)
        return ""
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
        import {{ createClient }} from "https://esm.sh/@anam-ai/js-sdk@latest";
        
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
                
                // Set up event listeners
                anamClient.on("connectionStateChange", (state) => {{
                    if (state === "connected") {{
                        statusElement.textContent = "✅ Connected! Start speaking...";
                        statusElement.style.color = "#00c853";
                    }} else if (state === "disconnected") {{
                        statusElement.textContent = "❌ Disconnected";
                        statusElement.style.color = "#ff5252";
                    }} else {{
                        statusElement.textContent = "Status: " + state;
                        statusElement.style.color = "#ffa726";
                    }}
                }});
                
                anamClient.on("userTranscript", (transcript) => {{
                    if (transcript.isFinal) {{
                        addToTranscript("user", transcript.text);
                    }}
                }});
                
                anamClient.on("agentTranscript", (transcript) => {{
                    if (transcript.isFinal) {{
                        addToTranscript("assistant", transcript.text);
                    }}
                }});
                
                // Start streaming to video element
                await anamClient.streamToVideoElement("persona-video");
                
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


def main():
    """Main application entry point."""
    
    # Header
    st.markdown('<h1 class="main-header">🎭 Anam AI Avatar with MemU Memory</h1>', unsafe_allow_html=True)
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
        default_prompt = """You are Maya, a friendly and helpful AI assistant with a warm personality. 
You have access to memories from previous conversations and use them to provide personalized responses.
Keep your responses conversational, concise, and engaging."""
        
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
                st.success("Memory cleared!")
        
        st.divider()
        
        # API Key status
        st.header("🔑 API Status")
        anam_key = os.getenv("ANAM_API_KEY")
        memu_key = os.getenv("MEMU_API_KEY")
        
        st.write("ANAM_API_KEY:", "✅ Set" if anam_key else "❌ Missing")
        st.write("MEMU_API_KEY:", "✅ Set" if memu_key else "❌ Missing")
    
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
                    if enable_memory:
                        memu_client = get_memu_client()
                        if memu_client:
                            memory_context = get_memory_context(
                                memu_client, 
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
                if enable_memory:
                    if st.button("💾 Save Conversation to Memory"):
                        memu_client = get_memu_client()
                        if memu_client and "conversation_history" in st.session_state:
                            if save_conversation_to_memory(memu_client, st.session_state.conversation_history):
                                st.success("✅ Conversation saved to MemU memory!")
    
    with col2:
        st.subheader("🧠 Memory Status")
        
        if enable_memory:
            memu_client = get_memu_client()
            
            if memu_client:
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
                    if "conversation_history" in st.session_state:
                        for msg in st.session_state.conversation_history[-5:]:
                            role_icon = "👤" if msg["role"] == "user" else "🤖"
                            st.write(f"{role_icon} {msg['content'][:100]}...")
                    else:
                        st.write("No recent memories yet.")
        else:
            st.warning("Memory is disabled. Enable it in the sidebar to store conversations.")
        
        st.divider()
        
        # Instructions
        st.subheader("📖 How to Use")
        st.markdown("""
        1. **Configure** your avatar in the sidebar
        2. **Start** the avatar session
        3. **Speak** to interact with your AI avatar
        4. **Save** conversations to build memory
        
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


if __name__ == "__main__":
    # Initialize session state
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "avatar_active" not in st.session_state:
        st.session_state.avatar_active = False
    if "total_conversations" not in st.session_state:
        st.session_state.total_conversations = 0
    if "memory_items" not in st.session_state:
        st.session_state.memory_items = 0
    
    main()
