# LightRAG Agent with Web UI

A modern conversational AI agent powered by LightRAG's graph-based retrieval capabilities, featuring a ChatGPT-like web interface for interacting with custom knowledge bases from Word documents.

## Overview

This project implements a full-stack LightRAG agent that allows users to:
- Upload Word documents (.docx) to create custom knowledge bases
- Chat with an AI agent that has contextual understanding of the uploaded content
- Experience real-time streaming responses with source attribution
- Manage multiple knowledge bases through a modern web interface

## Architecture

### Backend (Python/FastAPI)
- **LightRAG Integration**: Core graph-based retrieval system following [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) patterns
- **FastAPI Server**: RESTful API with WebSocket support for real-time chat
- **Document Processing**: Word document parsing, chunking, and knowledge graph construction
- **Vector Storage**: ChromaDB/Neo4j integration for embeddings and graph storage
- **Redis**: Session management and caching

### Frontend (React/Next.js)
- **Modern Chat UI**: ChatGPT-like interface with message bubbles and streaming responses
- **Document Upload**: Drag-and-drop interface with progress tracking
- **Real-time Updates**: WebSocket integration for live chat experience
- **Responsive Design**: Tailwind CSS with dark/light theme support

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Docker and Docker Compose (recommended)

### Development Setup

1. **Clone and enter the project directory:**
   ```bash
   git clone <your-repo-url>
   cd LightRAG_Agent
   ```

2. **Set up environment variables:**
   ```bash
   # Copy environment examples
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   
   # Add your API keys to the .env files
   # Required: OPENAI_API_KEY, ANTHROPIC_API_KEY (optional)
   ```

3. **Backend Setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   ```

5. **Start with Docker (Recommended):**
   ```bash
   # From project root
   docker-compose up --build
   ```

   **OR Start Services Individually:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   
   # Terminal 3 - Redis (if not using Docker)
   redis-server
   
   # Terminal 4 - Neo4j (if not using Docker)
   # Follow Neo4j installation instructions
   ```

6. **Access the Application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Usage

1. **Upload Documents**: Use the drag-and-drop interface to upload Word documents
2. **Wait for Processing**: Monitor the progress as documents are processed and knowledge graphs are built
3. **Start Chatting**: Ask questions about your uploaded content in natural language
4. **View Sources**: See which parts of your knowledge base were used to generate responses

## Project Structure

```
LightRAG_Agent/
├── frontend/                 # Next.js React application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   │   ├── chat/        # Chat interface components
│   │   │   └── upload/      # File upload components
│   │   ├── lib/             # Utility functions
│   │   └── types/           # TypeScript definitions
├── backend/                 # FastAPI Python application
│   ├── app/
│   │   ├── routers/         # API route handlers
│   │   ├── services/        # Business logic
│   │   ├── models/          # Data models
│   │   ├── config/          # Configuration
│   │   └── utils/           # Utility functions
│   ├── tests/               # Test files
│   └── requirements.txt     # Python dependencies
├── docker-compose.yml       # Docker services configuration
├── scripts/                 # Task Master configuration
└── tasks/                   # Project tasks and documentation
```

## Key Features

### Document Processing
- **Multi-format Support**: Primary focus on .docx with extensibility for PDF and other formats
- **Intelligent Chunking**: Context-aware text segmentation for optimal knowledge graph construction
- **Entity Extraction**: Automatic identification of key entities and relationships
- **Graph Construction**: Building knowledge graphs using LightRAG's advanced algorithms

### Chat Interface
- **Real-time Streaming**: Responses stream in real-time as they're generated
- **Message History**: Persistent chat history with session management
- **Markdown Support**: Rich text rendering with code syntax highlighting
- **Source Attribution**: Links to specific parts of the knowledge base used in responses

### Knowledge Management
- **Multiple Knowledge Bases**: Support for different document collections
- **Graph Visualization**: (Planned) Visual exploration of knowledge graphs
- **Export/Import**: (Planned) Knowledge base portability

## Environment Variables

### Backend (.env)
```env
# Required
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key  # Optional

# Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
REDIS_URL=redis://localhost:6379

# LightRAG Configuration
LIGHTRAG_MODEL=gpt-4
LIGHTRAG_EMBEDDING_MODEL=text-embedding-ada-002
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## API Endpoints

### Document Management
- `POST /api/documents/upload` - Upload and process documents
- `GET /api/documents` - List uploaded documents
- `DELETE /api/documents/{id}` - Remove documents

### Chat
- `POST /api/chat/query` - Send chat messages
- `WS /ws/chat/{session_id}` - WebSocket for real-time chat

### Knowledge Base
- `GET /api/knowledge-bases` - List knowledge bases
- `POST /api/knowledge-bases` - Create new knowledge base
- `GET /api/knowledge-bases/{id}/stats` - Knowledge base analytics

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style
- **Backend**: Black formatter, flake8 linting
- **Frontend**: ESLint, Prettier formatting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## References

- [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) - Core LightRAG implementation
- [ottomator-agents](https://github.com/coleam00/ottomator-agents/tree/main/light-rag-agent) - Reference architecture
- [Tutorial Video](https://youtu.be/Fx3J8k--U3E?si=2i7MM5DbKppuNcIu) - UI design inspiration

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For questions and support, please open an issue in the repository or refer to the documentation in the `tasks/` directory. 