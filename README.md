## Mizhavu Chat Bot

🚀 **[Try the Live Application Here](https://mizhavu-chatbot-using-rag.onrender.com)**

Mizhavu Chatbot is an educational chatbot created to educate people about the endangered musical instrument Mizhavu. It utilizes a Retrieval-Augmented Generation (RAG) architecture to provide accurate, context-aware information about the Mizhavu drum and the historic Kudiyattam theatre tradition.

## 🚀 Features

* **Advanced RAG Engine:** Retrieves precise context stored in an online Pinecone vector database.
* **Retriver provided as a tool:** The llm has the ability to decide whether to call the retriver node or answer using the chat history.
* **Document Processing:** Knowledge base source text was extracted from authoritative PDF documents using unstructured.io.
* **State-of-the-Art Embeddings:** Uses the `models/gemini-embedding-001` model by Google.
* **State Preservation & Memory:** Built-in persistence via LangGraph checkpointers preserves active session chat histories.
* **Agentic AI Workflow:** Orchestrates complex decisions via hierarchical subgraphs and specialized LLM nodes:
  * **Rephraser Agent:** Converts context-dependent user inputs into stand-alone queries.
  * **Bouncer Agent:** Filters incoming queries to ensure the chatbot stays on-topic (Mizhavu/Kudiyattam).
  * **Answer Generator:** Orchestrates tool calls and synthesizes history-aware responses.
  * **Off-Topic Agent:** Hand-shakes non-contextual yet relevant or chatbot-related questions in a friendly, engaging manner.
 
## 🛠️ Tech Stack

* **Frontend:** Next.js (React)
* **Backend:** FastAPI (Python)
* **AI Orchestration:** LangGraph & LangChain
* **Vector Database:** Pinecone
* **LLM & Embeddings:** Google Gemini API
---

## 📦 Installation

To run this project locally, you will need to install the dependencies for both the frontend and the backend.

### 1. Frontend (Next.js)
Navigate to the client directory and install the Node.js packages:

    cd client
    npm install

### 2. Backend (FastAPI & LangGraph)
Navigate to the server directory, set up your environment, and install the Python dependencies:

    cd server
    python -m venv .venv
    
    # On Windows: 
    .venv\Scripts\activate
    
    # On macOS/Linux: 
    source .venv/bin/activate
    
    pip install -r requirements.txt

---

## 💻 Usage

### 1. Environment Setup
Before starting the servers, create a `.env` file in the `server` directory and add your API keys:

    GOOGLE_API_KEY="your_google_gemini_api_key"
    PINECONE_API_KEY="your_pinecone_api_key"
    PINECONE_INDEX_NAME="your_pinecone_index_name"

### 2. Start the Backend Server
Navigate to the server folder and launch the FastAPI backend via Uvicorn:

    cd server
    uvicorn app:app --reload

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make to the Mizhavu Chatbot are **greatly appreciated**!

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

### How to Contribute

1. **Fork the Project**
   Click the "Fork" button at the top right of this page to create a copy of this repository in your own GitHub account.

2. **Create your Feature Branch**
   `git checkout -b feature/AmazingFeature`

3. **Commit your Changes**
   `git commit -m 'Add some AmazingFeature'`

4. **Push to the Branch**
   `git push origin feature/AmazingFeature`

5. **Open a Pull Request**
   Go to the original repository page and click on "Compare & pull request".

---

## 📄 License

MIT License

Copyright (c) 2026 balagopan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
