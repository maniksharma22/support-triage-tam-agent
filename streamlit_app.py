import streamlit as st
import requests

st.set_page_config(page_title="AI Technical Support & TAM Tooling", layout="wide")

st.title("AI-Powered Technical Support & TAM Tooling")
st.write("Internal tooling for Technical Support engineers and Technical Account Managers (TAMs).")

tab1, tab2, tab3, tab4 = st.tabs(["Ticket Triage", "Account Brief", "Knowledge Base Query", "Evaluation Harness"])

with tab1:
    st.header("Task 1: Intelligent Ticket Triage Agent")
    ticket_text = st.text_area("Enter Support Ticket (Subject + Body):", placeholder="Paste support ticket here...")
    if st.button("Triage Ticket"):
        if ticket_text:
            with st.spinner("Analyzing ticket..."):
                try:
                    response = requests.post("http://localhost:8000/triage", json={"ticket_text": ticket_text})
                    if response.status_code == 200:
                        res_json = response.json()
                        st.success("Triage Complete!")
                        st.json(res_json)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
        else:
            st.warning("Please enter ticket text.")

with tab2:
    st.header("Task 2: TAM Account Health Summariser")
    account_id = st.text_input("Enter Account ID:", placeholder="e.g., ACC-001")
    if st.button("Generate Brief"):
        if account_id:
            with st.spinner("Generating account brief..."):
                try:
                    response = requests.post("http://localhost:8000/account-brief", json={"account_id": account_id})
                    if response.status_code == 200:
                        res_json = response.json()
                        st.success("Brief Generated!")
                        st.json(res_json)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
        else:
            st.warning("Please enter an Account ID.")

with tab3:
    st.header("Knowledge Base Q&A")
    query_text = st.text_input("Ask a question about the product or documentation:")
    if st.button("Search KB"):
        if query_text:
            with st.spinner("Searching..."):
                try:
                    response = requests.post("http://localhost:8000/query", json={"query": query_text})
                    if response.status_code == 200:
                        st.info(response.json().get("answer", "No answer found."))
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
        else:
            st.warning("Please enter a query.")

with tab4:
    st.header("Task 3: Evaluation Harness")
    if st.button("Run Evaluation Suite"):
        with st.spinner("Running evaluations across test cases..."):
            try:
                response = requests.post("http://localhost:8000/run-eval")
                if response.status_code == 200:
                    st.success("Evaluation Completed!")
                    st.json(response.json())
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")