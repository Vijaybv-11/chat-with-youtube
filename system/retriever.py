


def retrieve(vector_store,search_type,search_kwargs):
    retriever=vector_store.as_retriever(search_type=search_type,search_kwargs=search_kwargs)
    return retriever