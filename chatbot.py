#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

load_dotenv('.env')
PATH_TO_DATABASE = os.environ.get('PATH_TO_DATABASE')

embeddings = OpenAIEmbeddings()
vectordb = Chroma(persist_directory=PATH_TO_DATABASE, embedding_function=embeddings)

# create our Q&A chain
pdf_qa = ConversationalRetrievalChain.from_llm(
    ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo'),
    retriever=vectordb.as_retriever(search_kwargs={'k': 6}),
    return_source_documents=True,
    verbose=False
)

yellow = "\033[0;33m"
green = "\033[0;32m"
white = "\033[0;39m"

chat_history = []
print(f"{yellow}--------------------------------------------------------------------------------------------")
print('Welcome to the VitalPBX Agent AI. You are now ready to start interacting with your documents')
print('                            Type exit, quit, q or f to finish                               ')
print('--------------------------------------------------------------------------------------------')
while True:
    query = input(f"{green}Prompt: ")
    if query == "exit" or query == "quit" or query == "q" or query == "f":
        print('Exiting')
        sys.exit()
    if query == '':
        continue
    result = pdf_qa(
        {"question": query, "chat_history": chat_history})
    print(f"{white}Answer: " + result["answer"])
    chat_history.append((query, result["answer"]))
