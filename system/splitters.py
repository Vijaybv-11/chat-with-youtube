
# 1.b Indexing  (Text Splitting)
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text,chunk_size=1000, overlap=200):
    """
    Splits the input text into chunks of specified size with optional overlap.

    Args:
        text (str): The input text to be split.
        chunk_size (int): The maximum size of each chunk. Default is 1000 characters.
        overlap (int): The number of overlapping characters between chunks. Default is 200 characters.

    Returns:
        list: A list of text chunks.
    """
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    chunks=text_splitter.split_text(text)
    return chunks