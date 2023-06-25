import os
import re
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from flask import Flask, render_template, request
from azure.storage.blob import BlobServiceClient

# Create a Flask application instance
app = Flask(__name__)

# Global variable for storing the index
index = None

# Function to preprocess a single document
def preprocess_document(document):
    # Remove non-ASCII characters
    document = document.encode("ascii", errors="ignore").decode()

    # Convert the text to lowercase
    document = document.lower()

    # Remove punctuation marks
    document = document.translate(str.maketrans("", "", string.punctuation))

    # Split the text into individual words or tokens
    tokens = document.split()

    # Remove stop words
    stop_words = set(stopwords.words("english"))
    tokens = [token for token in tokens if token not in stop_words]

    # Word stemming (optional)
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(token) for token in tokens]

    return tokens

# Function to preprocess all the documents in a directory
def preprocess_documents_from_blob_storage(connection_string, container_name):
    preprocessed_docs = []

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)

    # List all the blobs in the container
    blobs = container_client.list_blobs()

    # Iterate over the blobs and preprocess the documents
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob.name)
        document_content = blob_client.download_blob().readall().decode("utf-8")
        tokens = preprocess_document(document_content)
        preprocessed_docs.append(tokens)
        print(f"Preprocessed document: {tokens}")

    return preprocessed_docs

def build_index(preprocessed_docs):
    index = {}
    for doc_id, doc in enumerate(preprocessed_docs):
        for position, word in enumerate(doc):
            if word in index:
                index[word].append((doc_id, position))
            else:
                index[word] = [(doc_id, position)]
    return index

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for handling search requests
@app.route('/search', methods=['POST'])
def search():
    global index

    search_word = request.form['query']
    if index is not None and search_word in index:
        matching_documents = index[search_word]
        results = []
        for doc_id, position in matching_documents:
            result = {
                'document_id': doc_id,
                'position': position
            }
            results.append(result)
    else:
        results = []

    return render_template('results.html', results=results)

# Run the Flask application
if __name__ == '__main__':
    # Azure Blob Storage connection string and container name
    connection_string = "DefaultEndpointsProtocol=https;AccountName=sampl;AccountKey=GLijF+wF353BH7/A3FtGIegOfCfSYrMnZMtsTMT1N9euUX0VB7ihhrmbm+VFjZCZWI4lEos+yd/Q+AStwAJVcw==;EndpointSuffix=core.windows.net"
    container_name = "sampl1"

    # Preprocess the documents from Azure Blob Storage
    preprocessed_documents = preprocess_documents_from_blob_storage(connection_string, container_name)
    print("Preprocessed documents:")
    for i, doc in enumerate(preprocessed_documents):
        print(f"Document {i+1}: {doc}")

    # Build the index
    index = build_index(preprocessed_documents)

    app.run()
