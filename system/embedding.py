# Indexing (Embedding Generation and Storing in Vector Store)

from functools import lru_cache

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()


# loading the model takes a few seconds, so load it once and reuse it for every video
@lru_cache(maxsize=1)
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def generate_embeddings(chunks):
    vector_store = FAISS.from_texts(chunks, get_embedding_model())
    return vector_store
