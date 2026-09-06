prompt = """
You will receive a list of chunks. Use the information in the chunks to answer the question.

Chunks :
{chunks}

Question : 
{question}

Answer :
"""

def Get_prompt(chunks :list, question:str) -> str:
    return prompt.format(chunks = chunks , question = question)
