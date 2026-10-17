import requests
import streamlit as st

st.set_page_config(page_title="fin-rag", page_icon="📄")
st.title("📄 fin-rag: Ask Apple's 10-K")
st.caption("Hybrid retrieval + reranking over Apple's FY2025 10-K, answered by a local LLM with citations.")

mode = st.radio("Mode", ["fast", "accurate"], horizontal=True,
                help="fast = llama3.2:3b, accurate = qwen2.5:7b (slower, better at tables)")
question = st.text_input("Your question", "What was Apple's total net sales in 2025?")

if st.button("Ask") and question.strip():
    with st.spinner("Retrieving and generating..."):
        try:
            r = requests.post("http://127.0.0.1:8000/ask",
                              json={"question": question, "mode": mode}, timeout=600)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()
    st.subheader("Answer")
    st.write(data["answer"])
    st.caption(f"{data['mode']} mode, {data['seconds']} s")
    st.subheader("Sources")
    for s in data["sources"]:
        with st.expander(f"[{s['n']}] {s['chunk_id']} ({s['section']})"):
            st.text(s["text"])
