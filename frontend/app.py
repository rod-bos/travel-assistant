import streamlit as st
import requests

# Your FastAPI backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.set_page_config(page_title="Travel Assistant", layout="wide")

# Sidebar for uploads
with st.sidebar:
    st.title("📄 Documents")
    st.write("Upload travel documents:")
    
    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, DOCX",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True
    )

    if st.button("Ingest documents"):
        if not uploaded_files:
            st.warning("Please upload at least one file.")
        else:
            with st.spinner("Uploading and processing..."):
                files_payload = [
                    ("files", (f.name, f.getvalue(), f"type/{f.type}"))
                    for f in uploaded_files
                ]
                response = requests.post(f"{BACKEND_URL}/ingest", files=files_payload)
                
                if response.status_code == 200:
                    st.success("Files processed and vectorstore updated!")
                    st.json(response.json())
                else:
                    st.error("Error processing files.")


st.title("✈️ Travel Assistant")
st.markdown("Ask anything about your uploaded travel documents!")

# Display chat history
for entry in st.session_state.chat_history:
    st.markdown(f"**You:** {entry['user']}")
    st.markdown(f"**Assistant:** {entry['assistant']}")
# Show sources of the answer.
    sources = entry.get("sources", [])
    if sources:
        st.markdown("**Sources:**")
        st.write(sources)
    st.markdown("---")


# Input box
question = st.text_input("Your question:")

# Submit button
if st.button("Ask"):
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{BACKEND_URL}/ask",
                json={"question": question}
            )
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")

                # Save to session history
                st.session_state.chat_history.append({
                    "user": question,
                    "assistant": answer,
                    "sources": data.get("sources", [])
                })

                # Rerun UI to display updated chat
                st.rerun()
            else:
                st.error("Error while requesting answer from backend.")
                
                
