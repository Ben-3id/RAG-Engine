prompt = """
You will receive a list of chunks. Use the information in the chunks to answer the question.
do not make user feel u have resource for knowledge answer like you know.

Chunks :
{chunks}

Question : 
{question}

Answer :
"""

def Get_promptv2(chunks :list, question:str) -> str:
    return prompt.format(chunks = chunks , question = question)
