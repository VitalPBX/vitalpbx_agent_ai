#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

# Load environment variables from .env file
load_dotenv('.env')

# Define the path to the database
PATH_TO_DATABASE = os.environ.get('PATH_TO_DATABASE')

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Create a Chroma vector store
vectordb = Chroma(persist_directory=PATH_TO_DATABASE, embedding_function=embeddings)

# Create a Q&A chat chain
pdf_qa = ConversationalRetrievalChain.from_llm(
    ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo'),
    retriever=vectordb.as_retriever(search_kwargs={'k': 6}),
    return_source_documents=True,
    verbose=False
)

# Define text colors for console output
yellow = "\033[0;33m"
green = "\033[0;32m"
white = "\033[0;39m"

# Initialize chat history
chat_history = []

# Print welcome message and instructions
print(f"{yellow}--------------------------------------------------------------------------------------------")
print('Welcome to the VitalPBX Agent AI. You are now ready to start interacting with your documents')
print('                            Type exit, quit, q or f to finish                               ')
print('--------------------------------------------------------------------------------------------')

# Start the interactive chat loop
while True:
    query = input(f"{green}Prompt: ")
    
    # Check for exit commands
    if query == "exit" or query == "quit" or query == "q" or query == "f":
        print('Exiting')
        sys.exit()
    
    # Skip empty queries
    if query == '':
        continue
    
    # Perform document retrieval and answer generation
    result = pdf_qa(
        {"question": query, "chat_history": chat_history})
    
    # Display the answer
    print(f"{white}Answer: " + result["answer"])
    
    # Append the query and answer to chat history
    chat_history.append((query, result["answer"]))
