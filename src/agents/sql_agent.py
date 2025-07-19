import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import llm

def create_sql_agent():
    """
    Creates an agent that can query a SQL database.
    """
    logging.info("Creating SQL agent")
    
    system_prompt = (
        "You are an expert at querying a SQL database. "
        "Based on the user question and the database schema, write a SQL query "
        "to retrieve the requested information. "
        "Only respond with the SQL query, nothing else. "
        "Ensure the query is syntactically correct and optimized for SQLite. "
        "Use proper table and column names as specified in the schema."
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Question: {question}\n\nDatabase Schema: {schema}"),
        ]
    )
    
    agent = prompt | llm | StrOutputParser()
    logging.info("SQL agent created successfully")
    return agent
