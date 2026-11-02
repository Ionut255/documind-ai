
import chromadb
import streamlit as st

from embedding_utils import load_embedding_model


@st.cache_resource
def get_database():
    """Initialize an in-memory ChromaDB client."""
    return chromadb.EphemeralClient()


def store_chunks(chunks, embeddings, document_id, session_id):
    """Store document embeddings in a session-specific collection."""

    client = get_database()

    collection_name = (
        f"pdf_{session_id}_{document_id[:20]}"
    )

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=None
    )

    if collection.count() != len(chunks):
        embedding_list = embeddings.tolist()
        batch_size = 100

        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            end = start + len(batch)

            collection.upsert(
                ids=[
                    f"chunk_{i}"
                    for i in range(start, end)
                ],
                documents=[
                    chunk["text"]
                    for chunk in batch
                ],
                embeddings=embedding_list[start:end],
                metadatas=[
                    {
                        "page_number": chunk["page_number"],
                        "chunk_index": i
                    }
                    for i, chunk in enumerate(
                        batch, start=start
                    )
                ]
            )

    return collection_name


def search_chunks(collection_name, question, top_k=5):
    """Retrieve relevant chunks from the active collection."""

    client = get_database()

    collection = client.get_collection(
        name=collection_name,
        embedding_function=None
    )

    if collection.count() == 0:
        return []

    model = load_embedding_model()

    question_embedding = model.encode(
        question,
        normalize_embeddings=True,
        convert_to_numpy=True
    ).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    matches = []

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        matches.append({
            "text": text,
            "page_number": metadata["page_number"],
            "distance": float(distance)
        })

    return matches


def delete_collection(collection_name):
    """Remove a collection from temporary storage."""

    client = get_database()

    existing_collections = {
        collection.name
        for collection in client.list_collections()
    }

    if collection_name in existing_collections:
        client.delete_collection(name=collection_name)
