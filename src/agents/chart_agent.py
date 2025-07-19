import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import llm

def create_chart_agent():
    """
    Creates an agent that can generate code to create a chart.
    """
    logging.info("Creating chart agent")
    
    system_prompt = (
        "You are an expert at creating charts using matplotlib and seaborn. "
        "Based on the user question and the data, write Python code to generate "
        "a chart that answers the user's question. "
        "Only respond with the Python code, nothing else. "
        "Include necessary imports like 'import matplotlib.pyplot as plt' and 'import seaborn as sns'. "
        "Make sure the code is executable and creates a meaningful visualization. "
        "Use plt.show() at the end to display the chart."
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Question: {question}\n\nData: {data}"),
        ]
    )
    
    agent = prompt | llm | StrOutputParser()
    logging.info("Chart agent created successfully")
    return agent
