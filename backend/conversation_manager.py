import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import shutil
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

class ConversationManager:
    def __init__(self, storage_dir: str = "conversations"):
        self.storage_dir = storage_dir
        self.ensure_storage_directory()
        self.active_conversations: Dict[str, ConversationBufferMemory] = {}
        
    def ensure_storage_directory(self):
        """Ensure the storage directory exists"""
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def create_conversation(self, conversation_id: str) -> str:
        """Create a new conversation directory and initialize memory"""
        conv_dir = os.path.join(self.storage_dir, conversation_id)
        os.makedirs(conv_dir, exist_ok=True)
        os.makedirs(os.path.join(conv_dir, "files"), exist_ok=True)
        
        # Initialize conversation metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "message_count": 0
        }
        
        with open(os.path.join(conv_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f)
            
        # Initialize empty conversation history
        with open(os.path.join(conv_dir, "history.json"), "w") as f:
            json.dump([], f)
            
        # Initialize memory for this conversation
        self.active_conversations[conversation_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        return conversation_id
        
    def save_files(self, conversation_id: str, files: List[str]):
        """Save uploaded files for a conversation"""
        files_dir = os.path.join(self.storage_dir, conversation_id, "files")
        for file in files:
            shutil.copy2(file, files_dir)
            
    def save_interaction(self, conversation_id: str, human_message: str, ai_message: str):
        """Save a conversation interaction"""
        conv_dir = os.path.join(self.storage_dir, conversation_id)
        history_file = os.path.join(conv_dir, "history.json")
        
        # Load existing history
        with open(history_file, "r") as f:
            history = json.load(f)
            
        # Add new interaction
        history.append({
            "timestamp": datetime.now().isoformat(),
            "human_message": human_message,
            "ai_message": ai_message
        })
        
        # Save updated history
        with open(history_file, "w") as f:
            json.dump(history, f)
            
        # Update metadata
        metadata_file = os.path.join(conv_dir, "metadata.json")
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        metadata["last_updated"] = datetime.now().isoformat()
        metadata["message_count"] = len(history)
        
        with open(metadata_file, "w") as f:
            json.dump(metadata, f)
            
    def load_conversation(self, conversation_id: str) -> Optional[ConversationBufferMemory]:
        """Load a conversation's memory from storage"""
        if conversation_id in self.active_conversations:
            return self.active_conversations[conversation_id]
            
        conv_dir = os.path.join(self.storage_dir, conversation_id)
        if not os.path.exists(conv_dir):
            return None
            
        # Load history
        with open(os.path.join(conv_dir, "history.json"), "r") as f:
            history = json.load(f)
            
        # Create new memory instance
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Reconstruct memory from history
        for interaction in history:
            memory.chat_memory.messages.append(HumanMessage(content=interaction["human_message"]))
            memory.chat_memory.messages.append(AIMessage(content=interaction["ai_message"]))
            
        self.active_conversations[conversation_id] = memory
        return memory
        
    def list_conversations(self) -> List[Dict]:
        """List all conversations with their metadata"""
        conversations = []
        for conv_id in os.listdir(self.storage_dir):
            conv_dir = os.path.join(self.storage_dir, conv_id)
            if os.path.isdir(conv_dir):
                with open(os.path.join(conv_dir, "metadata.json"), "r") as f:
                    metadata = json.load(f)
                metadata["conversation_id"] = conv_id
                conversations.append(metadata)
        return conversations 