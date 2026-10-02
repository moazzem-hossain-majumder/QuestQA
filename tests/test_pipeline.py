"""Offline tests: no watsonx credentials needed (embeddings are faked)."""
from pathlib import Path

import pytest
from langchain_community.embeddings import DeterministicFakeEmbedding

import qabot

SAMPLE = Path(__file__).resolve().parent.parent / "sample_docs" / "sample_paper.pdf"


class _F:  # mimics a Gradio tempfile object
    name = str(SAMPLE)


@pytest.mark.parametrize("handle", [str(SAMPLE), _F()])
def test_document_loader_accepts_path_or_file_object(handle):
    docs = qabot.document_loader(handle)
    assert len(docs) >= 1
    assert "retrieval" in docs[0].page_content.lower()


def test_text_splitter_respects_chunk_size():
    chunks = qabot.text_splitter(qabot.document_loader(str(SAMPLE)))
    assert len(chunks) > 1
    assert all(len(c.page_content) <= 1000 for c in chunks)


def test_retriever_returns_relevant_chunks(monkeypatch):
    monkeypatch.setattr(qabot, "watsonx_embedding", lambda: DeterministicFakeEmbedding(size=64))
    r = qabot.retriever(str(SAMPLE))
    docs = r.invoke("How are documents split into chunks?")
    assert 1 <= len(docs) <= 4


def test_retriever_qa_validates_inputs():
    assert "upload" in qabot.retriever_qa(None, "hi").lower()
    assert "question" in qabot.retriever_qa(str(SAMPLE), "   ").lower()
