import secrets
import hashlib

import streamlit as st

from pdf_utils import (
    extract_pdf_pages,
    split_text_into_chunks
)
from embedding_utils import generate_embeddings
from database_utils import (
    store_chunks,
    search_chunks,
    delete_collection
)
from ai_utils import generate_answer


# Page configuration
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📄",
    layout="wide"
)

if "session_id" not in st.session_state:
    st.session_state["session_id"] = secrets.token_hex(12)

def get_api_key():
    """Load the Gemini API key."""
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except FileNotFoundError:
        return ""


def reset_conversation():
    """Clear the current conversation."""
    st.session_state["messages"] = []



def display_sources(sources):
    """Display cited document passages grouped by page."""

    if not sources:
        return

    pages = {}

    for source in sources:
        page = source["page_number"]

        if page not in pages:
            pages[page] = []

        # Avoid duplicate passages
        if not any(
            item["text"] == source["text"]
            for item in pages[page]
        ):
            pages[page].append(source)

    with st.expander("View Document Sources"):

        for page, passages in pages.items():
            st.markdown(f"### Page {page}")

            for passage in passages:
                st.write(passage["text"])

                st.caption(
                    f"Vector distance: "
                    f"{passage['distance']:.4f}"
                )

            st.divider()



# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# Sidebar
with st.sidebar:
    st.title("DocuMind AI")
    st.caption("Intelligent Document Assistant")

    st.divider()

    st.subheader("Document Upload")

    uploaded_file = st.file_uploader(
        "Upload a PDF document",
        type=["pdf"]
    )

    st.caption(
        "Supported format: PDF with selectable text."
    )


# Main interface
st.title("📄 DocuMind AI")
st.caption("Ask questions. Explore documents. Discover insights.")


if uploaded_file is None:
    st.session_state.pop("active_document_id", None)
    previous_data = st.session_state.get("document_data")

    if previous_data:
        delete_collection(previous_data["collection_name"])
    st.session_state.pop("document_data", None)
    reset_conversation()

    st.info(
        "Upload a PDF document using the sidebar "
        "to start your conversation."
    )
    st.stop()


# Identify the uploaded document
document_id = hashlib.sha256(
    uploaded_file.getvalue()
    + b"|all-MiniLM-L6-v2|chunk120|overlap25"
).hexdigest()[:24]


# Process a new document
if st.session_state.get("active_document_id") != document_id:

    try:
        with st.spinner("Analyzing your document..."):

            pages = extract_pdf_pages(uploaded_file)

            full_text = "\n\n".join(
                page["text"] for page in pages
            )

            if not full_text.strip():
                st.warning(
                    "No readable text found in this PDF."
                )
                st.stop()

            chunks = split_text_into_chunks(pages)

            embeddings = generate_embeddings(chunks)

            collection_name = store_chunks(
                chunks,
                embeddings,
                document_id,
                st.session_state["session_id"]
)
        previous_data = st.session_state.get("document_data")

        if previous_data:
            delete_collection(previous_data["collection_name"])
            
        st.session_state["document_data"] = {
            "pages": len(pages),
            "characters": len(full_text),
            "text": full_text,
            "chunks": chunks,
            "dimensions": embeddings.shape[1],
            "collection_name": collection_name
        }

        st.session_state["active_document_id"] = document_id

        reset_conversation()

    except Exception as error:
        st.error(f"Document processing failed: {error}")
        st.stop()


data = st.session_state["document_data"]


# Document information
with st.sidebar:
    st.divider()
    st.success("Document ready!")

    st.subheader("Document Information")
    st.write(f"**File:** {uploaded_file.name}")

    st.metric("Pages", data["pages"])
    st.metric("Text Chunks", len(data["chunks"]))
    st.metric("Embedding Dimensions", data["dimensions"])

    st.divider()

    if st.button(
        "Clear Conversation",
        use_container_width=True
    ):
        reset_conversation()
        st.rerun()

    with st.expander("Document Preview"):
        st.text_area(
            "Extracted Text",
            data["text"],
            height=250
        )


st.success("Your document is ready for AI-powered chat.")

st.divider()
st.subheader("Conversation")


# Display previous chat messages
for message in st.session_state["messages"]:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):
            display_sources(message["sources"])


# Load API key
api_key = get_api_key() 

if not api_key:
    st.warning(
        "Gemini API key is missing. "
        "Configure it in .streamlit/secrets.toml."
    )


# Chat input
prompt = st.chat_input(
    "Ask something about your document...",
    disabled=not bool(api_key)
)


if prompt:

    # Preserve recent conversation for follow-up questions
    previous_messages = st.session_state["messages"][-6:]

    previous_questions = [
        message["content"]
        for message in previous_messages
        if message["role"] == "user"
    ][-2:]

    # Include recent questions to improve follow-up retrieval
    search_query = " ".join(
        previous_questions + [prompt]
    )

    # Save and display the user's message
    st.session_state["messages"].append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate the AI response
    with st.chat_message("assistant"):

        try:
            with st.spinner("Thinking..."):

                matches = search_chunks(
                    data["collection_name"],
                    search_query,
                    top_k=5
                )

            answer, cited_sources = generate_answer(
            prompt,
            matches,
            api_key,
        history=previous_messages
    )

            st.markdown(answer)

            if cited_sources:
                display_sources(cited_sources)

            st.session_state["messages"].append({
                "role": "assistant",
                "content": answer,
                "sources": cited_sources
        })

        except Exception as error:
            st.error(
                f"Unable to generate an answer: {error}"
            )
