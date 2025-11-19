from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from api_key_extract import get_api_key
import streamlit as st

@st.cache_resource
def get_embedding_model():
    api_key = get_api_key()    
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )

def get_relavant_lines(prompt:str, paragraph_store:dict):
    
    embedding_function = get_embedding_model()
    vector_store = Chroma(
        embedding_function=embedding_function,
        persist_directory="chroma_db",
        collection_name="chatBot"
    )

    relavant_lines = vector_store.similarity_search_with_relevance_scores(
        prompt,
        k=3
    )

    parent_ids_to_fetch = set()

    for doc, score in relavant_lines:
        if score >= 0.89:
            parent_ids_to_fetch.add(doc.metadata["parent_id"])

    final_paragraph_list_for_llm = []

    for parent_id in parent_ids_to_fetch:
        if parent_id in paragraph_store:
            final_paragraph_list_for_llm.append(paragraph_store[parent_id])

    return final_paragraph_list_for_llm

