#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter

# Load environment variables from a .env file
load_dotenv("/var/lib/asterisk/agi-bin/.env")

# Retrieve paths and API keys from environment variables
PATH_TO_DOCUMENTS = os.environ.get('PATH_TO_DOCUMENTS')
PATH_TO_DATABASE = os.environ.get('PATH_TO_DATABASE')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Create an empty list to store documents
documents = []

# Create a List of Documents from all files in the PATH_TO_DOCUMENTS folder
for file in os.listdir(PATH_TO_DOCUMENTS):
    if file.endswith(".pdf"):
        pdf_path = PATH_TO_DOCUMENTS + file
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())
    elif file.endswith('.docx') or file.endswith('.doc'):
        doc_path = PATH_TO_DOCUMENTS + file
        loader = Docx2txtLoader(doc_path)
        documents.extend(loader.load())
    elif file.endswith('.txt'):
        text_path = PATH_TO_DOCUMENTS + file
        loader = TextLoader(text_path)
        documents.extend(loader.load())

# Split the documents into smaller chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
documents = text_splitter.split_documents(documents)

# Convert the document chunks to embeddings and save them to the vector store
vectordb = Chroma.from_documents(documents, embedding=OpenAIEmbeddings(), persist_directory=PATH_TO_DATABASE)
vectordb.persist()
