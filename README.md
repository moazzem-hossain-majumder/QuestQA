# QuestQA — Chat with Your PDFs using RAG, LangChain & watsonx.ai

A question-answering web app that reads a PDF you upload and answers questions about it in real time, grounded in the document's own text. It was built as the final project of IBM's Coursera course
[**Project: Generative AI Applications with RAG and LangChain**](https://www.coursera.org/learn/project-generative-ai-applications-with-rag-and-langchain/home/welcome),
where you play a consultant for *Quest Analytics*, a research organisation that needs to extract insights from large volumes of scientific literature.

## How it works

```
 PDF ──► document_loader ──► text_splitter ──► watsonx_embedding ──► vector_database (Chroma)
        (PyPDFLoader)     (RecursiveCharacter   (WatsonxEmbeddings,        │
                           TextSplitter)         IBM Slate 125M)           ▼
 Question ───────────────────────────────────────────────────────► retriever (similarity search)
                                                                           │ top-k chunks
                                                                           ▼
                                                  retriever_qa: RetrievalQA + get_llm() (WatsonxLLM)
                                                                           │
                                                                           ▼
                                                                  Gradio web interface
```

| Stage | Function in `qabot.py` | Component |
|-------|------------------------|-----------|
| 1. Load document | `document_loader(file)` | `PyPDFLoader` (`langchain_community`) |
| 2. Split text | `text_splitter(data)` | `RecursiveCharacterTextSplitter` (chunk size 1000, overlap 50) |
| 3. Embed | `watsonx_embedding()` | `WatsonxEmbeddings` (`langchain_ibm`), IBM Slate 125M English (`ibm/slate-125m-english-rtrvr-v2`) |
| 4. Vector store | `vector_database(chunks)` | `Chroma.from_documents()` |
| 5. Retrieve | `retriever(file)` | `vectordb.as_retriever()` (similarity search) |
| 6. Answer + UI | `retriever_qa(file, query)` + `gr.Interface` | `RetrievalQA` ("stuff" chain), `WatsonxLLM` (Granite), Gradio |

LLM settings: `ibm/granite-4-h-small`, temperature `0.5`, max new tokens `256`.

## Project structure

```
quest-qa-rag-bot/
├── qabot.py                  # the complete app (all six tasks + Gradio UI)
├── embedding_demo.py         # embeds a sentence, prints first 5 numbers (Task 3 screenshot)
├── requirements.txt
├── .env.example              # credentials template (copy to .env)
├── sample_docs/
│   └── sample_paper.pdf      # small demo PDF about RAG
├── scripts/make_sample_pdf.py
├── tests/test_pipeline.py    # offline tests (fake embeddings, no credentials needed)
└── screenshots/              # put your graded screenshots here
```

---

## How to test it locally (Windows + VS Code)

### 0. Prerequisites

- **Python 3.11** (3.10–3.12 also work). Check with `py --version`. Install from <https://www.python.org/downloads/> and tick **"Add python.exe to PATH"**.
- **VS Code** with the **Python** extension (by Microsoft).
- **Git**.
- An **IBM Cloud account** with **watsonx.ai** (see step 3). *Not needed if you only run the offline tests.*

### 1. Get the code and open it in VS Code

```powershell
git clone https://github.com/<your-username>/quest-qa-rag-bot.git
cd quest-qa-rag-bot
code .
```

Open a terminal in VS Code: **Terminal → New Terminal** (PowerShell).

### 2. Create a virtual environment and install dependencies

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- If PowerShell blocks activation ("running scripts is disabled"), run this once, then activate again:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
  (Or use Command Prompt and run `.venv\Scripts\activate.bat`.)
- In VS Code press **Ctrl+Shift+P → "Python: Select Interpreter"** and choose `.venv\Scripts\python.exe`.

### 3. Run the offline tests first (no credentials needed)

These check PDF loading, text splitting, and the retriever wiring using fake embeddings:

```powershell
pytest -q
```

Expected: `5 passed`. If this passes, your environment and dependencies are fine.

### 4. Add your watsonx.ai credentials (needed for the real app)

The default `skills-network` project only works **inside the IBM Skills Network lab IDE**. On your own PC you need your own account:

1. Go to <https://cloud.ibm.com> → create / sign in to an account.
2. Open **watsonx.ai** and create a **project**. In the project, open **Manage → General** and copy the **Project ID**. Make sure the project is linked to a **watsonx.ai Runtime** service instance (Manage → Services & integrations).
3. Create an API key at <https://cloud.ibm.com/iam/apikeys> (**Create +**) and copy it.
4. Create your env file and fill it in:

```powershell
copy .env.example .env
notepad .env
```

```
WATSONX_APIKEY=your-ibm-cloud-api-key
WATSONX_PROJECT_ID=your-watsonx-project-id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

> Use the URL for the region where your project lives (e.g. `https://eu-de.ml.cloud.ibm.com`). `.env` is git-ignored, so your key will not be pushed to GitHub.

### 5. Check the embedding model (quick credential test)

```powershell
python embedding_demo.py
```

You should see the vector dimension and the first five numbers. This is also your `embedding.png` screenshot. If this works, your credentials, project ID and region are correct.

### 6. Run the app

```powershell
python qabot.py
```

Open <http://localhost:7860> in your browser (not `0.0.0.0`). Then:

1. Upload `sample_docs/sample_paper.pdf` (or any short readable PDF).
2. Type: `What this paper is talking about?`
3. Click **Submit** and wait a few seconds for the answer.
4. Take the `QA_bot.png` screenshot (interface + uploaded PDF + query + answer).

Stop the server with **Ctrl+C** in the terminal.

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again |
| `ModuleNotFoundError` | Venv not active or wrong interpreter: re-activate and re-select it in VS Code, then `pip install -r requirements.txt` |
| `chromadb` / `chroma-hnswlib` build error | Use Python 3.11, upgrade pip, or install *Microsoft C++ Build Tools* |
| `401` / authentication error | Wrong or missing `WATSONX_APIKEY` in `.env` |
| `project_id` not found / no access | Wrong `WATSONX_PROJECT_ID`, or project not linked to a watsonx.ai Runtime service |
| Model not found / not supported | Pick an available model for your region and set `WATSONX_LLM_MODEL_ID` / `WATSONX_EMBEDDING_MODEL_ID` in `.env` |
| `ImportError: cannot import name 'RetrievalQA'` | You installed LangChain 1.x. Run `pip install -r requirements.txt` (pins `langchain` 0.3.x) |
| Port 7860 already in use | Close the other instance, or change `server_port` in `qabot.py` |
| Very slow / fails on a big PDF | Use a small PDF; the whole file is embedded on every question |

### Environment variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `WATSONX_APIKEY` | IBM Cloud API key (required outside the Skills Network lab) | — |
| `WATSONX_PROJECT_ID` | watsonx.ai project ID | `skills-network` |
| `WATSONX_URL` | watsonx.ai endpoint | `https://us-south.ml.cloud.ibm.com` |
| `WATSONX_LLM_MODEL_ID` | LLM model | `ibm/granite-4-h-small` |
| `WATSONX_EMBEDDING_MODEL_ID` | Embedding model | `ibm/slate-125m-english-rtrvr-v2` |

---

## Running inside the IBM Skills Network lab IDE

No API key needed; the code defaults to the lab's `skills-network` project.

```bash
cd /home/project
pip install virtualenv
virtualenv my_env && source my_env/bin/activate
pip install -r requirements.txt
python3.11 qabot.py
```

Then open **Skills Network extension → Launch Application → port `7860` → Your Application**.

---

## Screenshots for the peer-graded assignment

Save each screenshot in `screenshots/` with exactly these names:

| File | What to capture |
|------|-----------------|
| `pdf_loader.png` | the `document_loader` function in `qabot.py` |
| `code_splitter.png` | the `text_splitter` function |
| `embedding.png` | the `watsonx_embedding()` code, plus `python embedding_demo.py` output showing the first five numbers |
| `vectordb.png` | the `vector_database` function |
| `retriever.png` | the `retriever` function |
| `QA_bot.png` | the running Gradio app with a PDF uploaded and the query `What this paper is talking about?` answered |

---

## Final assignment answers (11 questions, 15 points)

| # | Question (short) | Answer | Pts |
|---|------------------|--------|-----|
| 1 | LangChain class used to load PDFs | **PyPDFLoader** | 1 |
| 2 | Why is the embedding model required when creating the Chroma vector DB? | **To convert document chunks into numerical vector representations** | 1 |
| 3 | Why a text splitter after `.load()`? | **Large documents must be split into smaller chunks for efficient processing by LLMs** | 1 |
| 4 | Which step makes chunks retrievable by similarity search? | **Creating a vector database using `vector_database(chunks)`** | 1 |
| 5 | True statements about `watsonx_embedding()` (select all) | ✅ The model `ibm/slate-125m-english-rtrvr-v2` is used to generate text embeddings<br>✅ `WatsonxEmbeddings` is imported from the `langchain_ibm` library<br>❌ ~~`TRUNCATE_INPUT_TOKENS` controls how many tokens are removed from the output embedding~~<br>✅ Embeddings generated by this model are vector representations of text chunks | 3 |
| 6 | Method to convert a vector DB into a retriever | **`vectordb.as_retriever()`** | 1 |
| 7 | Component that performs RAG question answering | **RetrievalQA** | 1 |
| 8 | Correct sequence of steps | **1, 5, 4, 2, 3, 6** (Document loader → Text splitter → Embedding model → Vector store → Define the retriever → QA chain and Gradio interface) | 1 |
| 9 | Role of `get_llm()` | **It initializes the large language model used to generate answers** | 1 |
| 10 | Upload `QA_bot.png` | Upload your own screenshot of the running Gradio app: PDF uploaded, query `What this paper is talking about?` entered, and the answer shown | 2 |
| 11 | Components used to interact with the user (select all) | ✅ **`gr.Textbox()`**, ✅ **`gr.File()`** (not `gr.Slider()` or `gr.Image()`) | 2 |

**Notes on the trickier ones**

- **Q4:** the retriever itself is created by `vectordb.as_retriever()`, but that option is not listed. Among the choices, the vector database built from the embedded chunks is what makes similarity search possible.
- **Q5:** `TRUNCATE_INPUT_TOKENS` limits the number of **input** tokens passed to the model (inputs longer than that are truncated). It does not remove tokens from the output embedding, so that statement is false.
- **Q8:** the order follows the lab tasks: load, split, embed, store, retrieve, then the QA chain and UI.

---

## Notes and limitations

- Very large PDFs can fail or be slow: the whole file is embedded on every query and held in an in-memory Chroma store.
- Answers are limited to 256 new tokens, as the lab specifies.
- The index is rebuilt for each question. For production use, build the vector store once per document and reuse it (e.g. a persistent Chroma directory).

## Credits

The task structure and starter code come from the IBM Skills Network lab *Construct a QA Bot that Leverages LangChain and LLMs to Answer Questions from Loaded Documents* (licensed under Apache 2.0). Built with [LangChain](https://python.langchain.com), [IBM watsonx.ai](https://www.ibm.com/products/watsonx-ai), [Chroma](https://www.trychroma.com) and [Gradio](https://www.gradio.app).