import streamlit as st
import requests
import json
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoint
API_URL = "http://localhost:8000"

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Page config
st.set_page_config(page_title="PDF Chatbot", layout="wide")
st.title("📚 Agentic RAG PDF Chatbot")

# Sidebar for document upload
with st.sidebar:
    st.header("Document Upload")
    uploaded_files = st.file_uploader("Upload your PDF documents", type=['pdf'], accept_multiple_files=True)
    
    if uploaded_files:
        with st.spinner("Processing documents..."):
            # Prepare files for upload
            files = [("files", file) for file in uploaded_files]
            
            try:
                # Upload files to API
                response = requests.post(f"{API_URL}/upload", files=files)
                response.raise_for_status()
                st.success("Documents processed successfully!")
            except requests.exceptions.RequestException as e:
                st.error(f"Error uploading documents: {str(e)}")

# Main chat interface
st.header("Chat Interface")

# Display conversation history
for message in st.session_state.conversation_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("View Sources"):
                for idx, source in enumerate(message["sources"], 1):
                    st.markdown(f"**Source {idx}:**")
                    st.write(source["page_content"])
                    if "metadata" in source:
                        st.write("Metadata:", source["metadata"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents"):
    # Add user message to chat history
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get chatbot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Prepare chat history for API
                chat_history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.conversation_history[:-1]  # Exclude current message
                ]
                
                # Send request to API
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"question": prompt, "chat_history": chat_history}
                )
                response.raise_for_status()
                result = response.json()
                
                # Display response
                st.write(result["answer"])
                
                # Add assistant message to chat history
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result.get("source_documents", [])
                })
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error getting response: {str(e)}")
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": f"Error: {str(e)}"
                })

# Add a clear button
if st.button("Clear Conversation"):
    st.session_state.conversation_history = []
    st.experimental_rerun()