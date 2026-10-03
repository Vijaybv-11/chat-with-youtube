from system.retriever import retrieve
from system.augmentation import augmenter
from system.generation import generate

def answer_question(vector_store,question):
    retriever=retrieve(vector_store,"similarity",{"k":4})
    retrieved_docs = retriever.invoke(question)
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    final_prompt=augmenter(context_text,question)
    answer=generate(final_prompt)
    return answer