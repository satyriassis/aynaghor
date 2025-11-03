import streamlit as st
import sys
import os
from datetime import datetime

# Add the root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import Engine
from modules.memory import MemoryManager
from modules.voice import VoiceProcessor
from modules.image import ImageProcessor

# Set page configuration
st.set_page_config(
    page_title="AYNAGH0R – Dark & Erotic AI",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        max-width: 80%;
    }
    .user-message {
        background-color: #1e3a5f;
        margin-left: auto;
        border-left: 4px solid #4ecdc4;
    }
    .assistant-message {
        background-color: #2d1b3d;
        margin-right: auto;
        border-left: 4px solid #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'engine' not in st.session_state:
    st.session_state.engine = Engine()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_mode' not in st.session_state:
    st.session_state.conversation_mode = "dark_erotic"

def display_chat_message(role, content):
    """Display a chat message with appropriate styling."""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>🧑‍💼 You:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    elif role == "assistant":
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🌙 AYNAGH0R:</strong><br>
            {content.replace(chr(10), "<br>")}
        </div>
        """, unsafe_allow_html=True)
    elif role == "system":
        st.info(f"System: {content}")

# Main header
st.markdown('<h1 class="main-header">🌙 AYNAGH0R</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #a8a8a8;">Dark & Erotic AI Storytelling Assistant</p>', unsafe_allow_html=True)

# Sidebar with controls
with st.sidebar:
    st.header("⚙️ Settings")

    # AI Provider Selection
    ai_provider = st.selectbox(
        "AI Provider",
        ["Local AI (Offline)", "Google Gemini"],
        help="Choose your AI provider"
    )

    # Conversation Mode
    st.session_state.conversation_mode = st.selectbox(
        "Conversation Mode",
        ["dark_erotic", "creative", "analytical"],
        help="Select the conversation style"
    )

    # Memory Management
    st.header("🧠 Memory")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Stats"):
            stats = st.session_state.engine.memory.get_statistics()
            st.json(stats)

    with col2:
        if st.button("🗑️ Clear"):
            st.session_state.engine.clear_conversation()
            st.session_state.messages = []
            st.success("Conversation cleared!")
            st.rerun()

    # Media Processing
    st.header("🎭 Media Processing")

    voice = VoiceProcessor()
    image = ImageProcessor()

    st.subheader("🎤 Voice")
    voice_features = voice.is_available()
    st.write(f"Speech-to-Text: {'✅' if voice_features['speech_to_text'] else '❌'}")
    st.write(f"Text-to-Speech: {'✅' if voice_features['text_to_speech'] else '❌'}")

    st.subheader("🖼️ Images")
    image_features = image.is_available()
    st.write(f"Image Analysis: {'✅' if image_features['image_analysis'] else '❌'}")
    st.write(f"Image Generation: {'✅' if image_features['image_generation'] else '❌'}")

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    # Chat interface
    st.header("💬 Conversation")

    # Display conversation history
    for message in st.session_state.messages:
        display_chat_message(message["role"], message["content"])

    # Input area
    st.markdown("---")

    # Text input
    user_input = st.text_area(
        "Your message:",
        placeholder="Enter your dark fantasy or erotic story prompt here...",
        height=100,
        key="user_input"
    )

    # Send button
    if st.button("🚀 Send", type="primary"):
        if user_input.strip():
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Generate response
            with st.spinner("🌙 AYNAGH0R is thinking..."):
                context = {
                    "mode": st.session_state.conversation_mode,
                    "conversation_history": st.session_state.messages[-5:]
                }

                try:
                    response = st.session_state.engine.route(
                        user_input,
                        context=context
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.session_state.messages.append({"role": "system", "content": error_msg})

            st.rerun()

with col2:
    # Quick Actions
    st.header("⚡ Quick Actions")

    if st.button("🎲 Random Prompt"):
        prompts = [
            "Tell me a dark fantasy story about forbidden love in ancient Rome",
            "Create an erotic tale set in a Victorian mansion",
            "Write about a mysterious encounter in a moonlit forest",
            "Describe a passionate affair between mortal and immortal beings",
            "Craft a story about desire and destiny in medieval times"
        ]
        import random
        st.session_state.user_input = random.choice(prompts)
        st.rerun()

    if st.button("📜 Story Starters"):
        starters = [
            "The moon hung heavy in the night sky as...",
            "In the shadows of the ancient cathedral...",
            "Her eyes held secrets that could undo kingdoms...",
            "The forbidden text spoke of rites long forgotten...",
            "Midnight brought with it whispers of desire..."
        ]
        import random
        st.session_state.user_input = random.choice(starters)
        st.rerun()

    # Export conversation
    if st.session_state.messages and st.button("💾 Save Chat"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aynaghor_chat_{timestamp}.json"

        try:
            # Export using memory manager
            export_file = st.session_state.engine.memory.export_conversation(filename)
            st.success(f"Conversation saved to {export_file}")
        except Exception as e:
            st.error(f"Failed to save conversation: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #666; font-size: 0.8rem;">'
    'AYNAGH0R v1.0.0 | Dark Fantasy & Erotic AI Storytelling | Use Responsibly'
    '</p>',
    unsafe_allow_html=True
)