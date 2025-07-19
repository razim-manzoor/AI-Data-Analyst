import logging
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from config import llm

def create_router_agent():
    """
    Creates a router agent that determines which specialist agent to use.
    """
    logging.info("Creating router agent")
    
    system_prompt = (
        "You are an expert at routing a user question to a specialist agent. "
        "Based on the user question, determine whether the user is asking a "
        "question that requires querying a database, or a question that requires "
        "creating a chart or visualization. "
        "If the user is asking for data, statistics, counts, or database queries, "
        "respond with 'sql'. "
        "If the user is asking for charts, graphs, plots, or visualizations, "
        "respond with 'chart'. "
        "Do not respond with any other words, only 'sql' or 'chart'. "
        "When in doubt, default to 'sql'."
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{question}"),
        ]
    )
    
    agent = prompt | llm | StrOutputParser()
    logging.info("Router agent created successfully")
    return agent
