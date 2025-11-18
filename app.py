from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from Chat_name import get_chat_name
from link_extractor import links_extractor, text_extraction_from_link
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from vector_db_store import store_to_vector_db
from retrieving_relevant_lines import get_relavant_lines 
from system_prompt_for_personality import personality
import time
import streamlit as st

@st.cache_resource
def get_model():
    load_dotenv()
    model = ChatGoogleGenerativeAI(
        # model="gemini-2.5-flash",
        model = "gemini-2.5-flash",
        temperature=0.5,
        max_output_tokens=150000
    )
    return model, StrOutputParser()

def stream(content, delay):
    for chunk in content:
        yield chunk
        time.sleep(delay)

st.set_page_config(
    initial_sidebar_state="collapsed",
    layout="centered",
    page_icon="🤖",
    page_title="Jena Bot"
)

if "chat_context" not in st.session_state:
    st.session_state.chat_context = 0

with st.sidebar:
    st.title("Jena Bot")
    with st.container(border=False, height=450):
        chat_context = str(st.session_state.chat_context)
        if not chat_context:
            chat_context = "chat_intelligence"
        st.button(
            label=chat_context,
            icon="💬",
            width="stretch",

        )


st.markdown("<h1 style='text-align: center;'>Enjoy the conversation</h1>", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "message_history" not in st.session_state:
    system_instruction = personality()
    st.session_state.message_history = [
        SystemMessage(content=system_instruction),
    ]

if "paragraph_store_with_ids" not in st.session_state:
    st.session_state.paragraph_store_with_ids = dict()

if "link_storage" not in st.session_state:
    st.session_state.link_storage = []

MAX_CHARACTER_LENGTH = 150

# Display all existing messages (without streaming for old messages)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            if len(message["content"]) > MAX_CHARACTER_LENGTH:
                snippet = message["content"][:MAX_CHARACTER_LENGTH] + "..."
                html_dropdown = f"""
                    <details>
                        <summary>{snippet}</summary>
                        {message["content"]}
                    </details>
                """
                st.markdown(html_dropdown, unsafe_allow_html=True)
            else:
                st.markdown(message["content"])
        else:
            st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask something!"):

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message immediately
    with st.chat_message("user"):
        if len(prompt) > MAX_CHARACTER_LENGTH:
            snippet = prompt[:MAX_CHARACTER_LENGTH] + "..."
            html_dropdown = f"""
                <details>
                    <summary>{snippet}</summary>
                    {prompt}
                </details>
            """
            st.markdown(html_dropdown, unsafe_allow_html=True)
        else:
            st.write_stream(stream(prompt,0.02))
    
    # Add to session state

    links = links_extractor(prompt)
    texts = []

    if links:
        for link in links:
            if link not in st.session_state.link_storage:
                texts.append(text_extraction_from_link(link=link))
                st.session_state.link_storage.append(link)

    print(texts)

    message_for_llm = st.session_state.message_history.copy()

    if texts:
        for text in texts:
            st.session_state.paragraph_store_with_ids |= store_to_vector_db(text)

    paragraph_store_with_ids = st.session_state.paragraph_store_with_ids.copy()
    final_paragraph_list_for_llm = get_relavant_lines(prompt=prompt, paragraph_store=paragraph_store_with_ids)
    print(final_paragraph_list_for_llm)
    if final_paragraph_list_for_llm:
        context_prompt = f"""
                            You are a helpful and precise assistant.
                            You will be given a block of context and a question.
                            Your task is to answer the user's question *using only* the provided context.

                            RULES:
                            1.  If the answer is in the context, quote the relevant part and provide a clear answer with a summarized way.
                            2.  If the answer is *not* in the context or this context is irrelavant, THEN YOU CAN LEAVE THIS SystemMessage PART!!!"
                            3.  Do not use any external knowledge or make up an answer.

                            Here is the context:
                            ---
                            {"\n\n".join(final_paragraph_list_for_llm)} 
                        """        
        message_for_llm.append(SystemMessage(content=context_prompt))

    if texts:
        for text in texts:
            message_for_llm.append(SystemMessage(content=text))

    message_for_llm.append(HumanMessage(content=prompt))

    # Get AI response and display with streaming
    model, parser = get_model()
    chain = model | parser

    with st.spinner("Summoning the intelligence..."):
        with st.chat_message("assistant"):
            response = chain.invoke(message_for_llm)
            st.write_stream(stream(response,0.01))
    
    # Add AI response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.message_history.append(HumanMessage(content=prompt))
    st.session_state.message_history.append(AIMessage(content=response))

    print(chat_context)
    if st.session_state.chat_context == 0 or not chat_context:
        chat_context = get_chat_name(st.session_state.messages[-2:len(st.session_state.messages)], model, parser)
        st.session_state.chat_context = chat_context

    print(len(st.session_state.message_history))
    st.rerun()