# Agentic RAG PDF Chatbot

A powerful chatbot application that uses RAG (Retrieval Augmented Generation) to intelligently answer questions about uploaded PDF documents. The system combines the power of LangChain, OpenAI's GPT models, and vector storage to provide accurate, context-aware responses.

## Features

- 📄 PDF Document Upload & Processing
- 💬 Interactive Chat Interface
- 🔍 Intelligent Document Search
- 🧠 Context-Aware Responses
- 📊 Conversation History Management
- 🎭 Customizable Assistant Personalities
- 🔗 Source Citations & References

## Technology Stack

### Backend
- FastAPI - Modern web framework for building APIs
- LangChain - Framework for developing applications powered by language models
- OpenAI GPT-4 - Advanced language model for generating responses
- FAISS - Vector storage for efficient document retrieval
- PyPDF - PDF document processing

### Frontend
- Streamlit - Interactive web interface
- Python Requests - HTTP client for API communication

## Project Structure

```
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── chat.py
│   │   │   ├── conversations.py
│   │   │   └── documents.py
│   │   └── models/
│   │       └── schemas.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── services/
│   │   ├── conversation.py
│   │   ├── document.py
│   │   └── chat.py
│   └── utils/
│       └── helpers.py
├── frontend/
│   ├── app.py
│   ├── config.py
│   └── components/
│       ├── chat.py
│       └── document_upload.py
├── config/
│   └── settings.py
└── docker/
    ├── backend.Dockerfile
    ├── frontend.Dockerfile
    └── docker-compose.yml
```

## Setup & Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf-chatbot.git
cd pdf-chatbot
```

2. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
OPENAI_API_KEY=your_openai_api_key
BACKEND_URL=http://localhost:8000
```

3. Using Docker (Recommended):
```bash
docker-compose up --build
```

4. Manual Setup:

Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Frontend:
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## Usage

1. Access the web interface at `http://localhost:8501`
2. Upload PDF documents using the sidebar
3. Start chatting with the bot about your documents
4. View source citations and references in the expandable sections
5. Clear conversations using the "Clear Conversation" button

## Configuration

The application can be configured through various settings:

- `config/settings.py` - Core application settings
- `.env` - Environment variables and API keys
- `.streamlit/config.toml` - Streamlit-specific configurations

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Security

- API keys and sensitive data are managed through environment variables
- Document storage is temporary and session-based
- Secure file handling and validation
- Rate limiting on API endpoints

## License

[Your License Here]

## Contact

[Your Contact Information]