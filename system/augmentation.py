from langchain_core.prompts import PromptTemplate
def augmenter(context,question):
    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.
        Answer ONLY from the provided transcript context.
        If the context is insufficient, just say you don't know.

        {context}
        Question: {question}
        """,
        input_variables = ['context', 'question']
    )
    return prompt.invoke({"context": context, "question": question})
