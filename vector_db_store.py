from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import uuid

# query = "what is Domicile certificate here?"
# text = """
#         Domicile Certificate: This specifically certifies you as a permanent resident of a state, implying a long-term intention to reside there and usually involves meeting a minimum residency duration criterion (e.g., 3 to 15 years, depending on the state). It grants access to permanent resident benefits like education and job quotas.
#         Residence Certificate: This term can sometimes be used more broadly or informally to mean any proof of current residence, which might be temporary in nature (e.g., utility bill or rent agreement).
#         """
def store_to_vector_db(text):
    load_dotenv()
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )
    paragraph_store = dict()

    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000, 
        chunk_overlap=400
    )

    child_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=300, 
        chunk_overlap = 20,
    )

    all_child_lines_for_vectorDB = []

    parent_paragraph = parent_splitter.split_text(text=text)

    for paragraph in parent_paragraph:
        parent_id = str(uuid.uuid4())
        paragraph_store[parent_id] = paragraph #storing paragraph

        child_lines = child_splitter.split_text(paragraph)
        for line in child_lines:
            line_document = Document(
                page_content=line,
                metadata = {
                    "parent_id" : parent_id
                }
            )
            all_child_lines_for_vectorDB.append(line_document)

    vector_store = Chroma.from_documents(
        documents=all_child_lines_for_vectorDB,
        embedding = embedding_model,
        persist_directory="chroma_db",
        collection_name="chatBot"
    )
    print("vectores are successfully stored to vector db!!")
    
    return paragraph_store