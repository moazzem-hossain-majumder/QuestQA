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
| 3. Embed | `watsonx_embedding()` | `WatsonxEmbeddings` (`langchain_ibm`), IBM Slate 125M English |
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

## Quick start

### Option A — IBM Skills Network Cloud IDE (the course lab)

No API key needed; the code defaults to the lab's `skills-network` project.

```bash
cd /home/project
pip install virtualenv
virtualenv my_env && source my_env/bin/activate
pip install -r requirements.txt
python3.11 qabot.py
```

Then open **Skills Network extension → Launch Application → port `7860` → Your Application**.

### Option B — Run locally with your own watsonx.ai account

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                    # then fill in your values
python qabot.py
```

Open <http://localhost:7860>, upload a PDF, type a question, and press **Submit**.

| Variable | Purpose | Default |
|----------|---------|---------|
| `WATSONX_APIKEY` | IBM Cloud API key (required outside the Skills Network lab) | — |
| `WATSONX_PROJECT_ID` | watsonx.ai project ID | `skills-network` |
| `WATSONX_URL` | watsonx.ai endpoint | `https://us-south.ml.cloud.ibm.com` |
| `WATSONX_LLM_MODEL_ID` | LLM model | `ibm/granite-4-h-small` |
| `WATSONX_EMBEDDING_MODEL_ID` | Embedding model | `ibm/slate-125m-english-rtrvr` |

> Model availability depends on your watsonx.ai region. If a model ID is rejected, pick one from the
> [watsonx.ai foundation model list](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models.html) and set the variable above.

## Tests

The tests run fully offline (embeddings are faked), so they verify loading, splitting, and the retriever wiring without credentials:

```bash
python scripts/make_sample_pdf.py   # only needed if sample_docs/sample_paper.pdf is missing
pytest -q
```

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

## Notes and limitations

- Very large PDFs can fail or be slow: the whole file is embedded on every query and held in an in-memory Chroma store.
- Answers are limited to 256 new tokens, as the lab specifies.
- The index is rebuilt for each question. For production use, build the vector store once per document and reuse it (e.g. a persistent Chroma directory).

## Credits

The task structure and starter code come from the IBM Skills Network lab *Construct a QA Bot that Leverages LangChain and LLMs to Answer Questions from Loaded Documents* (licensed under Apache 2.0). Built with [LangChain](https://python.langchain.com), [IBM watsonx.ai](https://www.ibm.com/products/watsonx-ai), [Chroma](https://www.trychroma.com) and [Gradio](https://www.gradio.app).
