
# DocuMind AI

### Chat with Your Documents

DocuMind AI is an AI-powered PDF question-answering
application built with Retrieval-Augmented Generation
(RAG).

Upload a PDF, ask questions in natural language, and
receive context-aware answers supported by references
to the original document.

## Features

- PDF document upload and text extraction
- Automatic text chunking with overlap
- Semantic embeddings using Sentence Transformers
- Vector storage and retrieval with ChromaDB
- AI-generated answers powered by Google Gemini
- Conversational chat with follow-up questions
- Conversation history within the current session
- Document references with original page numbers
- Expandable source passages
- Conversation reset functionality
- Interactive Streamlit interface

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Application logic |
| Streamlit | Web interface |
| Google Gemini | AI answer generation |
| Sentence Transformers | Text embeddings |
| ChromaDB | Vector search |
| PyPDF | PDF text extraction |
| NumPy | Numerical operations |

## How It Works

1. The user uploads a PDF document.
2. Text is extracted from its pages.
3. The text is split into overlapping chunks.
4. Each chunk is transformed into an embedding.
5. Embeddings are stored in ChromaDB.
6. The user's question is converted into an embedding.
7. Relevant document chunks are retrieved.
8. Gemini generates an answer using the retrieved context.
9. The answer is displayed with document page references.

## Project Structure

    pdf-rag-chatbot/
    ├── app.py
    ├── ai_utils.py
    ├── database_utils.py
    ├── embedding_utils.py
    ├── pdf_utils.py
    ├── requirements.txt
    ├── .gitignore
    └── README.md

## Installation

### 1. Clone the repository

    git clone https://github.com/Ionut255/documind-ai.git
    cd documind-ai

### 2. Create a virtual environment

    python -m venv .venv

Activate it on Windows:

    .\.venv\Scripts\activate

Or on macOS/Linux:

    source .venv/bin/activate

### 3. Install dependencies

    python -m pip install -r requirements.txt

### 4. Configure the Gemini API key

Create a `.streamlit/secrets.toml` file:

    GEMINI_API_KEY = "YOUR_API_KEY"

Get an API key from Google AI Studio.

Never commit API keys or secrets to GitHub.

### 5. Run the application

    streamlit run app.py

Open http://localhost:8501 in your browser.

## Usage

1. Upload a PDF document using the sidebar.
2. Wait for document processing to finish.
3. Enter a question in the chat interface.
4. Read the AI-generated answer.
5. Expand the document sources to inspect relevant passages.
6. Ask follow-up questions or clear the conversation.

## Current Limitations

- Text-based PDFs are supported; scanned PDFs may require OCR.
- The embedding model works best with English text.
- Conversation history is limited to the active session.
- AI-generated answers may contain mistakes.
- The local in-memory vector store is intended for demonstration.
- Uploaded documents should not contain confidential information.

## Future Improvements

- Support for multiple documents
- OCR for scanned PDFs
- Multilingual document embeddings
- Improved source attribution
- Additional document formats
- User authentication and stronger data isolation

## Security

The Gemini API key is stored outside the Git repository
using Streamlit Secrets Management.

The public demo is intended for non-sensitive documents.
For confidential or production use, additional access
controls, data isolation, and retention safeguards
are required.

## License

No license has been assigned yet.
