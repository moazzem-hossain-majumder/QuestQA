"""Generate sample_docs/sample_paper.pdf (a short fake 'paper' on RAG) for demos and tests."""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

TITLE = "Retrieval-Augmented Generation for Scientific Literature Assistants"
SECTIONS = {
    "Abstract": (
        "This paper presents a retrieval-augmented generation (RAG) assistant that answers questions "
        "about scientific documents. Instead of relying only on what a large language model memorised "
        "during training, the system retrieves relevant passages from a PDF at query time and supplies "
        "them to the model as context. We describe the full pipeline: document loading, text splitting, "
        "embedding, vector storage, retrieval and answer generation, and we discuss how each design "
        "choice affects answer quality and latency."
    ),
    "1. Introduction": (
        "Research organisations produce and consume enormous volumes of papers, reports and manuals. "
        "Reading all of them is impossible, and keyword search often misses relevant passages that use "
        "different vocabulary. Large language models can summarise and explain text, but they may "
        "hallucinate facts that are not in the source. RAG reduces this risk by grounding the answer "
        "in retrieved evidence from the user's own documents."
    ),
    "2. Method": (
        "Documents are first loaded page by page. Because a full page is too long to embed precisely "
        "and may exceed the context window of the model, the text is split into overlapping chunks of "
        "about one thousand characters. Each chunk is converted into a dense vector with an embedding "
        "model, so that chunks with similar meaning are close together in vector space. The vectors "
        "are stored in a vector database. At question time the query is embedded with the same model "
        "and the nearest chunks are returned by similarity search. These chunks are inserted into a "
        "prompt together with the question, and the language model writes the final answer."
    ),
    "3. Results": (
        "On a small internal benchmark the RAG assistant answered factual questions about the loaded "
        "papers more accurately than the same model without retrieval, and it could point to the "
        "passages that supported each answer. Chunk size and overlap were the most important "
        "hyper-parameters: very small chunks lost context, while very large chunks diluted the "
        "similarity signal and increased prompt length."
    ),
    "4. Conclusion": (
        "We conclude that a modular RAG pipeline built from standard components is a practical way to "
        "give researchers fast, grounded access to a large collection of documents. Future work will "
        "explore hybrid retrieval, re-ranking, and citations displayed in the user interface."
    ),
}


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "sample_docs" / "sample_paper.pdf"
    out.parent.mkdir(exist_ok=True)
    styles = getSampleStyleSheet()
    story = [Paragraph(TITLE, styles["Title"]), Spacer(1, 12)]
    for heading, body in SECTIONS.items():
        story += [Paragraph(heading, styles["Heading2"]), Paragraph(body, styles["BodyText"]), Spacer(1, 8)]
    SimpleDocTemplate(str(out), pagesize=A4).build(story)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
