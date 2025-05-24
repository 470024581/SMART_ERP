# SmartERP - Intelligent AI-Powered ERP Assistant

SmartERP is a modern web application designed to extend traditional ERP functionalities with an intelligent Q&A interface and dynamic data source management. It allows users to query various data sources, including structured ERP data, uploaded documents (PDF, DOCX, TXT), and CSV/Excel files, using natural language.

## Features

**1. Data Source Management:**
*   **Centralized Control:** Interface to list, create, activate, and delete data sources.
*   **Multiple Data Source Types:**
    *   **Default ERP:** Connects to the core structured ERP database (simulated with SQLite).
    *   **Knowledge Base/Documents (RAG):** Upload PDF, DOCX, TXT files. Queries are handled using Retrieval Augmented Generation (RAG) with local sentence embeddings (e.g., `intfloat/multilingual-e5-small`) and an in-memory FAISS vector store.
    *   **Formatted Data Table (CSV/Excel SQL Query):** Upload CSV or XLSX files. The system automatically ingests these into dedicated SQLite tables, which can then be queried via natural language processed by a LangChain SQL Agent.
*   **File Management:** Drag-and-drop file uploads, view file status (pending, processing, completed, failed), and delete files. File processing is handled asynchronously.
*   **Dynamic Activation:** Set any configured data source as "active" for the Q&A module.
*   **Sample Data:** Provides downloadable sample CSV sales data for testing.

**2. Intelligent Q&A Assistant:**
*   **Natural Language Querying:** Ask questions in plain English or Chinese to the active data source.
*   **Contextual Responses:** The system routes queries to the appropriate backend logic:
    *   **RAG:** For unstructured document collections.
    *   **SQL Agent:** For CSV/Excel-based SQL tables.
    *   **Direct DB Queries:** For the default ERP data.
*   **Dynamic Example Queries:** UI suggests relevant example queries based on the active data source type.
*   **Interactive Dropdown:** Users can view and change the active data source directly from the Q&A page.
*   **Response Display:** Shows AI-generated answers, supporting data (JSON), and query history.
*   **LLM Integration:** Leverages Large Language Models (potentially via Ollama for local models) for understanding queries and generating responses.

**3. Internationalization (i18n):**
*   Frontend supports English and Chinese languages, switchable via a UI control.

## Technical Stack

*   **Backend:**
    *   **Framework:** FastAPI
    *   **Language:** Python
    *   **Database:** SQLite (for application metadata, default ERP data, and dynamically created tables from CSV/Excel)
    *   **AI/NLP:**
        *   LangChain (for RAG, SQL Agents, LLM interaction)
        *   Sentence Transformers (for local text embeddings)
        *   FAISS (for vector similarity search in RAG)
        *   Pandas (for CSV/Excel data handling)
        *   PyPDF2, python-docx (for file parsing)
    *   **Async:** `aiofiles` for asynchronous file operations.
    *   **Dependencies:** See `server/requirements.txt`

*   **Frontend:**
    *   **Framework:** React (with Vite)
    *   **Language:** JavaScript (JSX)
    *   **UI Library:** React Bootstrap
    *   **State Management:** React Hooks (`useState`, `useEffect`)
    *   **Internationalization:** `react-i18next`, `i18next`
    *   **Icons:** React Icons
    *   **Dependencies:** See `client/package.json`

*   **Development Environment:**
    *   Requires Python 3.8+
    *   Requires Node.js and npm (or yarn)

## Project Structure
