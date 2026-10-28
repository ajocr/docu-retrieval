import streamlit as st
from answer import answer

st.title("Documentation Q&A for Powertools for AWS Lambda (Python)")
st.caption("Answers come only from the Powertools docs, with numbered citations.")

question = st.text_input("Ask a question about Powertools")

if question:
    with st.spinner("Searching the docs..."):
        result = answer(question)

    st.subheader("Answer")
    st.write(result["answer"])

    st.subheader("Sources")
    for n, hit in enumerate(result["hits"], start=1):
        st.write(f"[{n}] {hit['source']} — {hit['section']} (score {hit['score']:.3f})")

    st.subheader("Retrieved context")
    for n, hit in enumerate(result["hits"], start=1):
        with st.expander(f"[{n}] {hit['section']}"):
            st.text(hit["text"])
