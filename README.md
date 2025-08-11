# Academic RAG Pipeline with LLM Integration

A retrieval-augmented generation (RAG) system designed for academic research papers. Combines intelligent text chunking, vector search, and local LLM capabilities to provide context-aware responses to research queries.

##  Features

- **Intelligent Text Chunking**: Section-aware paper splitting using research paper  structure detection
- **Vector Search**: Pinecone integration for semantic similarity search
- **Local LLM Integration**: Ollama-powered language model with RAG augmentation
- **Modern Chat Interface**: Full-screen black & white UI with RAG toggle
- **ArXiv Integration**: Direct paper search and PDF processing
- **Smart Context Management**: Automatic relevance scoring and chunk selection

##  Architecture

```
pipeline/
├── ragpipe/                 # Core RAG pipeline
│   ├── services/           # Business logic services
│   │   ├── arxiv_service.py    # ArXiv API integration
│   │   ├── pdf_service.py      # PDF processing & text extraction
│   │   ├── rag_service.py      # RAG orchestration
│   │   ├── section_chunker.py  # Intelligent text chunking
│   │   └── vector_service.py   # Pinecone vector operations
│   ├── models/             # Data models
│   │   └── paper.py            # Academic paper representation
│   ├── config/             # Configuration management
│   │   └── settings.py         # App-wide settings
│   └── utils/              # Utility functions
│       └── text_cleaner.py     # Text preprocessing
├── llm_integration/        # LLM service layer
│   ├── services/           # LLM services
│   │   ├── llm_service.py      # Ollama integration
│   │   ├── rag_orchestrator.py # RAG + LLM coordination
│   │   └── prompt_builder.py   # Context-aware prompts
│   ├── models/             # Conversation models
│   ├── config/             # LLM configuration
│   └── main.py             # Main application entry
├── chat_app.py             # Flask web interface
├── templates/               # HTML templates
└── requirements.txt         # Python dependencies
```

##  Prerequisites

- **Python 3.8+**
- **Ollama** with **llama2:7b** model
- **Pinecone** account and API key
- **ArXiv** API access

##  Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pipeline
   ```

2. **Create and activate conda environment**
   ```bash
   conda create -n pipeline python=3.9
   conda activate pipeline
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama and pull model**
   ```bash
   # Install Ollama (macOS)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull the required model
   ollama pull llama2:7b
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
ENVIRONMENT=your_pinecone_environment
INDEX=your_index_name

# LLM Configuration
LLM_MODEL=llama2:7b
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=120

# RAG Settings
MAX_CONTEXT_LENGTH=4000
RAG_SIMILARITY_THRESHOLD=0.7
DEFAULT_SIMILARITY_THRESHOLD=0.4
```

### Key Configuration Parameters

- **`OLLAMA_TIMEOUT`**: Increased to 120s to handle RAG context processing
- **`DEFAULT_SIMILARITY_THRESHOLD`**: Set to 0.4 for academic paper relevance
- **`MAX_CONTEXT_LENGTH`**: Limits context to prevent LLM timeouts

##  Usage

### 1. Start Ollama Service

```bash
ollama serve
```

### 2. Run the Chat Interface

```bash
python chat_app.py
```

The application will start on `http://localhost:5001`

### 3. Using the RAG System

- **RAG Mode ON**: Queries search your paper database and provide context-augmented responses
- **RAG Mode OFF**: Direct LLM responses without paper context
- **Toggle**: Use the RAG toggle switch in the chat header

### 4. Command Line Testing

```bash
# Test the RAG pipeline
python -m ragpipe.main

# Test section chunking
python test_section_chunker.py

# Test chunked RAG integration
python test_chunked_rag.py
```

##  Core Components

### Section Chunker

Intelligent text splitting based on academic paper structure:
- Detects numbered sections (1. Introduction, 2.1 Background)
- Identifies common academic headers (Abstract, Methods, Results)
- Filters out tiny chunks (< 50 characters)
- Configurable chunk sizes (default: 2000 chars max, 50 chars min)

### RAG Service

Coordinates the complete retrieval pipeline:
- Vector database search with quality assessment
- ArXiv paper discovery when needed
- PDF processing and text extraction
- Intelligent chunk selection and relevance scoring

### LLM Integration

Local language model with RAG capabilities:
- Ollama integration for privacy and performance
- Context-aware prompt building
- Conversation history management
- Automatic RAG/LLM routing based on query type

## Data Flow

1. **User Query** → Chat interface
2. **RAG Processing** → Vector search + paper retrieval
3. **Text Chunking** → Section-aware splitting
4. **Relevance Scoring** → Semantic similarity + header matching
5. **Context Building** → Top-N relevant chunks
6. **LLM Generation** → Context-augmented response

## Testing

The project includes test scripts:

- **`test_section_chunker.py`**: Validates text chunking quality
- **`test_chunked_rag.py`**: Tests RAG pipeline integration
- **`test_pdf_content.py`**: Verifies PDF text extraction
- **`ragpipe/main.py`**: End-to-end pipeline testing

##  Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Ensure `ollama serve` is running
   - Check `OLLAMA_BASE_URL` in configuration

2. **Pinecone Connection Error**
   - Verify API key and environment settings
   - Check index name configuration

3. **PDF Processing Issues**
   - Ensure `PyPDF2` is installed
   - Check download directory permissions

4. **Timeout Errors**
   - Increase `OLLAMA_TIMEOUT` for complex queries
   - Reduce `max_chunks` in RAG service
