import os
import tempfile
from typing import List, Dict
import uuid
import json

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

# LangChain and OpenAI imports
from langchain_community.document_loaders import PyPDFLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage

from conversation_manager import ConversationManager

app = FastAPI(title="PDF Chatbot API")

# Global variables
conversation_manager = ConversationManager()
vector_stores: Dict[str, FAISS] = {}
agents: Dict[str, any] = {}

def build_system_prompt(assistant_name: str, assistant_behavior: str, custom_instructions: str) -> str:
    """
    Returns a string to be used as the system prompt, incorporating
    the assistant_name, assistant_behavior, and any custom instructions.
    """
    behavior_prompts = {
        "Professional": "You are a professional and formal assistant, providing clear and precise information.",
        "Friendly": "You are a friendly and approachable assistant, using conversational language while remaining informative.",
        "Academic": "You are an academic assistant, providing detailed, well-structured responses with scholarly precision.",
        "Creative": "You are a creative assistant, offering unique perspectives while remaining informative.",
        "Concise": "You are a concise assistant, providing brief but comprehensive answers.",
        "Detailed": "You are a detailed assistant, providing thorough and comprehensive explanations.",
        "Funny": "You are a funny assistant, providing all the wanted details in a clear way but with a funny twist or a joke in all of your responses"
    }

    base_prompt = f"""You are {assistant_name}, a helpful AI assistant specialized in analyzing and answering questions about PDF documents.
{behavior_prompts.get(assistant_behavior, behavior_prompts["Professional"])}

When answering questions:
1. Use the provided document context to formulate accurate responses
2. Cite specific sections from the documents when relevant
3. Maintain a consistent tone aligned with your {assistant_behavior.lower()} personality
4. Always know that 99% of the time, the answer will be in the provided documents (vectorstore) because you are built for a RAG app.
5. Iterate on the vector store querying until you find all the relevant details
6. If information is not found in the documents, clearly state that

Remember to always base your responses on the provided document context while maintaining your assigned personality.

{f"Always follow these custom instructions: {custom_instructions}" if custom_instructions else ""}
"""
    return base_prompt

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class NewConversationResponse(BaseModel):
    conversation_id: str
    message: str

@app.post("/conversations/new", response_model=NewConversationResponse)
async def create_conversation():
    """Create a new conversation and return its ID"""
    conversation_id = str(uuid.uuid4())
    conversation_manager.create_conversation(conversation_id)
    return NewConversationResponse(
        conversation_id=conversation_id,
        message="New conversation created successfully"
    )

@app.get("/conversations")
async def list_conversations():
    """List all conversations"""
    return conversation_manager.list_conversations()

@app.post("/conversations/{conversation_id}/upload")
async def upload_documents(conversation_id: str, files: List[UploadFile] = File(...)):
    """Upload documents for a specific conversation"""
    try:
        # Create a temporary directory for processing files
        with tempfile.TemporaryDirectory() as temp_dir:
            documents = []
            temp_files = []
            
            for file in files:
                temp_file_path = os.path.join(temp_dir, file.filename)
                with open(temp_file_path, "wb") as f:
                    f.write(await file.read())
                temp_files.append(temp_file_path)
                loader = PyPDFLoader(temp_file_path)
                docs = loader.load()
                documents.extend(docs)
            
            # Save files to conversation storage
            conversation_manager.save_files(conversation_id, temp_files)
            
            # Process documents
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            
            embeddings = OpenAIEmbeddings()
            vector_stores[conversation_id] = FAISS.from_documents(texts, embeddings)
            
            # Create retrieval tool
            retriever = vector_stores[conversation_id].as_retriever(search_kwargs={"k": 5})
            def search_docs(query: str) -> str:
                docs = retriever.invoke(query)
                return "\n\n".join([doc.page_content for doc in docs])
            
            retrieval_tool = Tool(
                name="Document Search",
                func=search_docs,
                description="Use this tool to search the uploaded documents for relevant information."
            )
            
            # Load or create memory for this conversation
            memory = conversation_manager.load_conversation(conversation_id)
            if not memory:
                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            
            # Initialize the agent
            llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
            agents[conversation_id] = initialize_agent(
                tools=[retrieval_tool],
                llm=llm,
                agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                verbose=True,
                memory=memory,
                handle_parsing_errors=True
            )
            
        return {"message": "Documents uploaded and processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    question: str
    assistant_name: str = "AI Assistant"
    assistant_behavior: str = "Professional"
    custom_instructions: str = ""

@app.post("/conversations/{conversation_id}/chat")
async def chat_endpoint(conversation_id: str, chat_req: ChatRequest):
    """Chat with a specific conversation"""
    if conversation_id not in agents:
        # Try to load the conversation if it's not loaded
        try:
            await load_conversation_documents(conversation_id)
        except Exception:
            pass
        
        if conversation_id not in agents:
            return {"answer": "No documents have been uploaded for this conversation. Please upload documents first."}
    
    agent = agents[conversation_id]
    memory = conversation_manager.load_conversation(conversation_id)
    
    system_prompt_text = build_system_prompt(
        chat_req.assistant_name,
        chat_req.assistant_behavior,
        chat_req.custom_instructions
    )

    # Update system message
    system_msgs = [m for m in memory.chat_memory.messages if m.type.lower() == "system"]
    if system_msgs:
        system_msgs[0].content = system_prompt_text
    else:
        memory.chat_memory.messages.insert(0, SystemMessage(content=system_prompt_text))

    try:
        result = agent.invoke(chat_req.question)
        output = result.get("output")
        
        # Save the interaction
        conversation_manager.save_interaction(
            conversation_id,
            chat_req.question,
            output
        )
        
        return {"answer": output}
    except Exception as e:
        return {"answer": f"An error occurred: {str(e)}"}

@app.get("/conversations/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """Get the chat history for a specific conversation"""
    try:
        conv_dir = os.path.join(conversation_manager.storage_dir, conversation_id)
        history_file = os.path.join(conv_dir, "history.json")
        
        if not os.path.exists(history_file):
            return {"messages": []}
            
        with open(history_file, "r") as f:
            history = json.load(f)
            
        # Convert the history format to match the frontend's expected format
        messages = []
        for interaction in history:
            messages.extend([
                {"role": "user", "content": interaction["human_message"]},
                {"role": "assistant", "content": interaction["ai_message"]}
            ])
            
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}/files")
async def get_conversation_files(conversation_id: str):
    """Get the list of files associated with a conversation"""
    try:
        conv_dir = os.path.join(conversation_manager.storage_dir, conversation_id)
        files_dir = os.path.join(conv_dir, "files")
        
        if not os.path.exists(files_dir):
            return {"files": []}
            
        # Get list of files in the conversation's files directory
        files = []
        for filename in os.listdir(files_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(files_dir, filename)
                files.append({
                    "filename": filename,
                    "size": os.path.getsize(file_path),
                    "uploaded_at": os.path.getctime(file_path)
                })
                
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def load_conversation_documents(conversation_id: str):
    """Load and process documents for an existing conversation"""
    try:
        conv_dir = os.path.join(conversation_manager.storage_dir, conversation_id)
        files_dir = os.path.join(conv_dir, "files")
        
        if not os.path.exists(files_dir):
            return
            
        documents = []
        for filename in os.listdir(files_dir):
            if filename.endswith('.pdf'):
                file_path = os.path.join(files_dir, filename)
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                documents.extend(docs)
        
        if documents:
            # Process documents
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            
            embeddings = OpenAIEmbeddings()
            vector_stores[conversation_id] = FAISS.from_documents(texts, embeddings)
            
            # Create retrieval tool
            retriever = vector_stores[conversation_id].as_retriever(search_kwargs={"k": 5})
            def search_docs(query: str) -> str:
                docs = retriever.invoke(query)
                return "\n\n".join([doc.page_content for doc in docs])
            
            retrieval_tool = Tool(
                name="Document Search",
                func=search_docs,
                description="Use this tool to search the uploaded documents for relevant information."
            )
            
            # Load or create memory for this conversation
            memory = conversation_manager.load_conversation(conversation_id)
            if not memory:
                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            
            # Initialize the agent
            llm = ChatOpenAI(model_name="gpt-4", temperature=0)
            agents[conversation_id] = initialize_agent(
                tools=[retrieval_tool],
                llm=llm,
                agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                verbose=True,
                memory=memory,
                handle_parsing_errors=True
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversations/{conversation_id}/load")
async def load_conversation(conversation_id: str):
    """Load a conversation's documents and initialize its agent"""
    try:
        await load_conversation_documents(conversation_id)
        return {"message": "Conversation loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
