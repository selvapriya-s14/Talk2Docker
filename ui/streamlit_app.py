from pathlib import Path
import streamlit as st
from agent.agent_loop import run_agent_turn
from rag.retriever import Retriever


st.set_page_config(page_title="Talk2Docker v2", layout="wide")

base_dir = Path(__file__).resolve().parents[1]
retriever = Retriever(base_dir / "rag" / "docker_docs", base_dir / "memory")

st.title("Talk2Docker v2")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask about Docker or run a command...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("assistant"):
        result = run_agent_turn(user_input, retriever)
        st.write(result["display"])
        if result.get("mode") == "knowledge":
            st.expander("RAG context").write("\n\n".join(result.get("context", [])))
        st.session_state.messages.append({"role": "assistant", "content": result["display"]})
