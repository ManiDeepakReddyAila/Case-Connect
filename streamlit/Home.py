import os
import streamlit as st
import requests
from dotenv import load_dotenv
from langchain.llms import OpenAI
from PIL import Image
load_dotenv()

img = Image.open('case_connect.jpg')
st.set_page_config(page_title="Case Connect")

col1, col2 = st.columns([1,3])

with col1:
    st.image(img, width = 170)
with col2:
    st.title('Case Connect')
    st.subheader('An Innovative Legatech')


st.markdown("---")


vector_search, graph_search = st.tabs(["Vector Search", "Graph Search"])

with vector_search:
    st.header("How can I help you today?")
    st.warning(
        "Disclaimer: Please note that the system's suggestions are for informational purposes only; users are advised to conduct their own research and seek professional legal advice for accurate interpretation and decision-making.")

    ques = [
        "What are my options if I get injured at work in a hazardous job?",
        "What steps should I take if my insurance company denies my claim for damages after a car accident?",
        "What are the elements I need to prove to establish medical malpractice against my surgeon?",
        "What legal options are available to companies dealing with environmental contamination at their facilities?",
        "What are the legal requirements for notifying an insurance company about a lawsuit against their insured party?",
        "Can someone appeal a decision about sharing information in court, and when can they do that?"
    ]
    with st.expander("**:orange[Example Questions:]**"):
        for i in range(len(ques)):
            st.code(ques[i], language='text')

    text = st.text_area("Enter your text")
    url = "http://localhost:8000/semantic_query"
    question = text
    if st.button("Submit"):
        if question:
            payload = {'question': question}
            res = requests.post(url, json=payload)
            data = {}
            if res.status_code == 200:
                data = res.json()
            else:
                st.error(res.text)
            response = data['answer']
            if response:
                question = """
                    Read the opinion text carefully to understand the key points and arguments presented in the case.
                    Summarize the case in a few sentences, focusing on the main facts, legal issues, and arguments discussed.
                    Determine the judgment or outcome of the case based on the information provided in the opinion text. Identify whether the court ruled in favor of the plaintiff or defendant, and any significant legal implications of the judgment.
                    Additional Guidance:

                    Use clear and concise language in your summary.
                    Focus on capturing the essential details of the case, including parties involved, legal claims, and court decisions.
                    Pay attention to any precedent-setting aspects or legal principles established by the case.
                    If necessary, consult legal resources or case law databases to ensure accuracy in summarizing and interpreting the judgment.

                    Example Output:

                    - Case ID: [Case ID of the case] \n
                    - Citation: [Citation of the case] \n
                    - Summary: [Brief summary of the case] \n
                    - Judgment: [Outcome of the case, e.g., "The court ruled in favor of the plaintiff, finding that [reasoning]."]

                    Please write each of the above in a new line.
                    """
                prompt = f"""Given the provided opinion text for a legal case, please include Case ID, Citation, a concise summary of the case and determine its judgment.

                    Opinion Text: {response}

                    Instructions:
                    {question} 
                    """
                st.write('**:blue[Answer]:** ' + response)
                try:
                    llm = OpenAI(temperature=0, openai_api_key=os.environ.get("OPENAI_API_KEY"))
                    ans = llm(prompt)
                    st.subheader("**:blue[Here's a case you can refer]**")
                    st.write(ans)

                except Exception as e:
                    st.error(e)
                    pass

with graph_search:
    st.header("Do you want to go deeper & utilise the power of graph search?")
    st.subheader("Convert natural languages queries to SQL queries")
    st.info("Powered by Chat2SQL, TiDb")

    ques = [
        'List the case_names of all "Medical Malpractice Case" cases in bullet format.',
        'How many "Criminal Case" cases are reported?',
        'What is the total count of cases registered?'
    ]
    with st.expander("**:orange[Example Questions:]**"):
        for i in range(len(ques)):
            st.code(ques[i], language='text')

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        url = "http://localhost:8000/graph_query"
        question = prompt
        payload = {'question': question}
        res = requests.post(url, json=payload)
        data = {}
        if res.status_code == 200:
            data = res.json()
        else:
            st.error(res.text)
        query = data['query']
        response = f"""Echo: \nCypher Query: {query} \nResult:\n{data['answer']}"""
        with st.chat_message("assistant"):
            st.text(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    if clear := st.button("Clear"):
        st.session_state.messages = []
        st.rerun()



