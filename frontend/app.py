import streamlit as st
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoint
API_URL = "http://backend:8000"

# Initialize session state
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'assistant_name' not in st.session_state:
    st.session_state.assistant_name = "AI Assistant"
if 'assistant_behavior' not in st.session_state:
    st.session_state.assistant_behavior = "Professional"
if 'custom_instructions' not in st.session_state:
    st.session_state.custom_instructions = ""
if 'conversations_list' not in st.session_state:
    st.session_state.conversations_list = []
if 'conversation_files' not in st.session_state:
    st.session_state.conversation_files = []

# Page config
st.set_page_config(
    page_title="PDF Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/pdf-chatbot',
        'Report a bug': "https://github.com/yourusername/pdf-chatbot/issues",
        'About': """
        # PDF Document Chatbot
        
        This is an AI-powered chatbot that helps you interact with your PDF documents.
        Upload documents and ask questions to get intelligent responses based on the content.
        """
    }
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #262730;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #4A4E69;
        color: #FAFAFA;
        border: 1px solid #666B85;
    }
    
    .stButton>button:hover {
        background-color: #666B85;
        border-color: #808495;
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        border-radius: 10px !important;
        border-color: #4A4E69 !important;
        background-color: #262730 !important;
        color: #FAFAFA !important;
        padding: 0.5em 1em !important;
        height: 40px !important;
        font-size: 1em !important;
    }
    
    /* Welcome message container */
    .upload-text {
        text-align: center;
        padding: 2em;
        background-color: #262730;
        border-radius: 10px;
        margin: 1em 0;
        border: 1px solid #4A4E69;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .upload-text h3 {
        color: #FAFAFA;
        margin-bottom: 1em;
    }
    
    .upload-text p, .upload-text li {
        color: #E0E0E0;
        font-size: 1.1em;
        line-height: 1.6;
    }
    
    /* Chat message containers */
    .stChatMessage {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #4A4E69;
        border-radius: 10px;
        padding: 1em;
        margin: 0.5em 0;
    }
    
    /* Chat message content */
    .stChatMessage div[data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    
    .stChatMessage div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }
    
    /* User message specific styling */
    [data-testid="chat-message-container"][data-testid="user-message"] {
        background-color: #1E3A5F !important;
    }
    
    /* Assistant message specific styling */
    [data-testid="chat-message-container"][data-testid="assistant-message"] {
        background-color: #2C2C3A !important;
    }
    
    /* Source expander styling */
    .streamlit-expanderContent {
        background-color: #1E1E1E !important;
        color: #ffffff !important;
        border-radius: 5px;
        padding: 10px;
    }
    
    /* Code blocks in sources */
    .streamlit-expanderContent code {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
        padding: 0.2em 0.4em;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        border-radius: 20px;
        border: 2px solid #4A4E69;
        padding: 0.5em;
        background-color: #262730;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #262730;
        border-radius: 10px;
        color: #FAFAFA;
    }
    
    /* Code block styling */
    code {
        background-color: #1E1E1E;
        color: #E0E0E0;
        padding: 0.2em 0.4em;
        border-radius: 4px;
    }
    
    /* Source document styling */
    .stExpander {
        background-color: #262730;
        border-radius: 10px;
        border: 1px solid #4A4E69;
    }
    
    /* Info message styling */
    .stAlert {
        background-color: #1E3A5F;
        color: #9EC2FF;
        border: none;
        border-radius: 10px;
    }
    
    /* Error message styling */
    .stException {
        background-color: #3D1919;
        color: #FF9E9E;
        border: none;
        border-radius: 10px;
    }
    
    /* Success message styling */
    .element-container:has(div.stAlert) {
        background-color: #193D1A;
        color: #9EFF9E;
        border-radius: 10px;
        padding: 1em;
    }
    
    /* Select box styling */
    .stSelectbox>div>div {
        background-color: #262730;
        color: #FAFAFA;
    }
    
    /* Text area styling */
    .stTextArea>div>div>textarea {
        background-color: #262730;
        color: #FAFAFA;
        border-color: #4A4E69;
    }
    
    /* Force all text to be white */
    p, div, span, li, h1, h2, h3, h4, h5, h6 {
        color: #FAFAFA !important;
    }
    
    /* Message sender label */
    .message-sender {
        font-size: 0.8em;
        color: #9E9E9E !important;
        margin-bottom: 5px;
        font-weight: 500;
    }
    
    /* Chat message containers with different colors */
    .stChatMessage[data-testid="user-message"] {
        background-color: #1E3A5F !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #2C2C3A !important;
    }
    
    /* Settings status indicator */
    .settings-status {
        padding: 8px;
        background-color: #262730;
        border-radius: 8px;
        margin-top: 10px;
        border: 1px solid #4A4E69;
        font-size: 0.9em;
    }
    
    .settings-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-right: 5px;
        background-color: #1E3A5F;
    }
    
    /* Sources styling */
    .streamlit-expanderContent {
        max-width: 300px !important;
        float: right !important;
        margin-left: auto !important;
        font-size: 0.9em !important;
        background-color: #1E1E1E !important;
    }
    
    .source-expander {
        margin-left: auto !important;
        width: fit-content !important;
        min-width: 200px !important;
    }
    
    /* Make source content more compact */
    .source-content {
        font-size: 0.85em !important;
        padding: 5px !important;
        margin: 2px 0 !important;
    }

    /* Sources icon button styling */
    .sources-icon {
        position: absolute;
        right: 10px;
        top: 5px;
        font-size: 1.2em;
        cursor: pointer;
        opacity: 0.7;
        transition: opacity 0.3s;
    }

    .sources-icon:hover {
        opacity: 1;
    }

    /* Sources content styling */
    .streamlit-expanderContent {
        position: absolute;
        right: 40px;
        top: 0;
        max-width: 300px !important;
        max-height: 400px !important;
        overflow-y: auto;
        font-size: 0.8em !important;
        background-color: #1E1E1E !important;
        border: 1px solid #4A4E69;
        border-radius: 5px;
        padding: 8px !important;
        z-index: 1000;
    }

    /* Hide default expander styling */
    .streamlit-expander {
        border: none !important;
        background: none !important;
        box-shadow: none !important;
    }

    .streamlit-expander > div:first-child {
        display: none !important;
    }

    /* Message container needs relative positioning */
    .stChatMessage {
        position: relative;
    }

    /* Source content text */
    .source-content {
        font-size: 0.85em !important;
        padding: 3px !important;
        margin: 2px 0 !important;
    }

    /* Code blocks in sources */
    .source-content code {
        font-size: 0.85em !important;
        padding: 2px 4px !important;
        background-color: #2D2D2D !important;
    }
    </style>
""", unsafe_allow_html=True)

def create_new_conversation():
    """Create a new conversation and set it as current"""
    try:
        response = requests.post(f"{API_URL}/conversations/new")
        if response.status_code == 200:
            data = response.json()
            st.session_state.current_conversation_id = data["conversation_id"]
            st.session_state.conversation_history = []
            return True
    except Exception as e:
        st.error(f"Failed to create new conversation: {str(e)}")
        return False

def load_conversations():
    """Load all conversations from the backend"""
    try:
        response = requests.get(f"{API_URL}/conversations")
        if response.status_code == 200:
            st.session_state.conversations_list = response.json()
    except Exception as e:
        st.error(f"Failed to load conversations: {str(e)}")

def load_conversation_history(conversation_id: str):
    """Load conversation history from the backend"""
    try:
        response = requests.get(f"{API_URL}/conversations/{conversation_id}/history")
        if response.status_code == 200:
            data = response.json()
            st.session_state.conversation_history = data["messages"]
    except Exception as e:
        st.error(f"Failed to load conversation history: {str(e)}")

def load_conversation_files(conversation_id: str):
    """Load files associated with a conversation"""
    try:
        response = requests.get(f"{API_URL}/conversations/{conversation_id}/files")
        if response.status_code == 200:
            data = response.json()
            st.session_state.conversation_files = data["files"]
    except Exception as e:
        st.error(f"Failed to load conversation files: {str(e)}")

def format_file_size(size_in_bytes: int) -> str:
    """Format file size to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.1f} TB"

def format_datetime(datetime_str: str) -> str:
    """Format datetime string to a more readable format"""
    # Split into date and time
    date_part, time_part = datetime_str.split("T")
    # Get hours and minutes from time
    time_part = time_part.split(".")[0]  # Remove milliseconds
    hours, minutes, _ = time_part.split(":")
    return f"{date_part} {hours}:{minutes}"

def switch_conversation(conversation_id: str):
    """Switch to a different conversation"""
    st.session_state.current_conversation_id = conversation_id
    st.session_state.conversation_history = []
    st.session_state.conversation_files = []  # Clear existing files
    
    # Show loading message
    with st.spinner("Loading conversation..."):
        try:
            # Load the conversation documents and initialize the agent
            response = requests.post(f"{API_URL}/conversations/{conversation_id}/load")
            if response.status_code != 200:
                st.error("Failed to load conversation documents")
                return
                
            # Load conversation history and files
            load_conversation_history(conversation_id)
            load_conversation_files(conversation_id)
            
        except Exception as e:
            st.error(f"Error loading conversation: {str(e)}")

# Sidebar for conversations
with st.sidebar:
    st.title("💬 Conversations")
    
    # New conversation button
    if st.button("New Conversation", key="new_conv"):
        create_new_conversation()
        st.rerun()
    
    # Load and display conversations
    load_conversations()
    
    if st.session_state.conversation_files:
        st.divider()
        st.subheader("📎 Conversation Files")
        for file in st.session_state.conversation_files:
            st.markdown(
                f"""
                <div style='padding: 10px; background-color: #262730; border-radius: 5px; margin: 5px 0;'>
                    <div style='font-weight: bold;'>📄 {file['filename']}</div>
                    <div style='font-size: 0.8em; color: #9E9E9E;'>
                        Size: {format_file_size(file['size'])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("Previous Conversations:")
    for conv in st.session_state.conversations_list:
        conv_id = conv["conversation_id"]
        created_at = format_datetime(conv["created_at"])
        message_count = conv["message_count"]
        
        # Create a unique key for each button
        if st.button(
            f"📄 {created_at} ({message_count} messages)",
            key=f"conv_{conv_id}",
            help=f"Conversation ID: {conv_id}"
        ):
            switch_conversation(conv_id)
            st.rerun()

    st.divider()
    
    # Assistant settings
    st.subheader("Assistant Settings")
    
    # Assistant name
    previous_name = st.session_state.assistant_name
    st.session_state.assistant_name = st.text_input(
        "Assistant Name",
        value=st.session_state.assistant_name
    )
    
    # Behavior selection
    previous_behavior = st.session_state.assistant_behavior
    behavior_options = [
        "Professional",
        "Friendly",
        "Academic",
        "Creative",
        "Concise",
        "Detailed",
        "Funny"
    ]
    st.session_state.assistant_behavior = st.selectbox(
        "Assistant Behavior",
        options=behavior_options,
        index=behavior_options.index(st.session_state.assistant_behavior)
    )
    
    # Custom instructions
    previous_instructions = st.session_state.custom_instructions
    st.session_state.custom_instructions = st.text_area(
        "Custom Instructions",
        value=st.session_state.custom_instructions,
        help="Add any specific instructions or context for the assistant"
    )
    
    # Settings status indicator
    settings_changed = (
        previous_name != st.session_state.assistant_name or
        previous_behavior != st.session_state.assistant_behavior or
        previous_instructions != st.session_state.custom_instructions
    )
    
    st.markdown("""
        <div class='settings-status'>
            <div class='settings-badge'>Status</div>
            {}
        </div>
    """.format(
        "⚠️ Changes not applied. Upload a document or start a new chat to apply changes."
        if settings_changed else
        "✅ Current settings are active"
    ), unsafe_allow_html=True)
    
    # Document upload section
    st.header("📄 Document Upload")
    uploaded_files = st.file_uploader(
        "Upload your PDF documents",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Process Documents"):
            with st.spinner("Processing documents..."):
                files = [("files", file) for file in uploaded_files]
                try:
                    response = requests.post(
                        f"{API_URL}/conversations/{st.session_state.current_conversation_id}/upload",
                        files=files
                    )
                    if response.status_code == 200:
                        st.success("Documents processed successfully!")
                    else:
                        st.error(f"Error processing documents: {response.text}")
                except Exception as e:
                    st.error(f"Error uploading documents: {str(e)}")

# Main chat interface
st.title("📚 PDF Document Chatbot")

# Create new conversation if none exists
if not st.session_state.current_conversation_id:
    create_new_conversation()

# Display conversation history
for message in st.session_state.conversation_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents"):
    # Add user message to chat history
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/conversations/{st.session_state.current_conversation_id}/chat",
                    json={
                        "question": prompt,
                        "assistant_name": st.session_state.assistant_name,
                        "assistant_behavior": st.session_state.assistant_behavior,
                        "custom_instructions": st.session_state.custom_instructions
                    }
                )
                if response.status_code == 200:
                    answer = response.json()["answer"]
                    st.write(answer)
                    st.session_state.conversation_history.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")