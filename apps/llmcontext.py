import os
from typing import Any
from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chat_models import ChatOpenAI

# Initialize the Chat model with OpenAI API key
OPENAI_API_KEY = "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"
chat_model = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

host = "db_host"
db_username = "username"
db_password = "password"
db_name = "db_name"


SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{db_username}:{db_password}@{host}/{db_name}"

# Construct the database URI
endpoint_id = host.split('.')[0]  # Extracting the endpoint ID
db_uri = f"postgresql+psycopg2://{db_username}:{db_password}@{host}/{db_name}?sslmode=require&options=endpoint%3D{endpoint_id}"

# Initialize database and chain
database = SQLDatabase.from_uri(db_uri, include_tables=['hotel'], sample_rows_in_table_info=2)
db_chain = SQLDatabaseChain.from_llm(chat_model, database, verbose=True)

def retrieve_from_db(query) -> Any:
    """
    Retrieves data from the database based on the provided query.
    
    Args:
        query (str): SQL query string.

    Returns:
        Any: The result of the database query.
    """
    try:
        db_context = db_chain(query)
        return db_context
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

print("Database context retrieved successfully.")

