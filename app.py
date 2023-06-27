import os
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from flask import Flask, render_template, request
from azure.storage.blob import BlobServiceClient

nltk.download('stopwords')

# Create a Flask application instance
app = Flask(__name__)

# Declare the global variable for the index
index = {}
preprocessed_documents = []  # Add a global variable for preprocessed documents


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

    return preprocessed_docs


def build_index(preprocessed_docs):
    index = {}
    for doc_id, doc in enumerate(preprocessed_docs):
        for position, word in enumerate(doc):
            if word in index:
                index[word].append((doc_id, [position]))  # Store positions as a list
            else:
                index[word] = [(doc_id, [position])]
    return index



def get_paragraphs(document_id, positions):
    # Implement this function to extract the relevant paragraphs from the document
    # based on the start and end positions
    # You can load the document content using the document_id and extract the paragraphs accordingly
    # Return a list of paragraphs

    # Example implementation (replace with your own logic):
    paragraphs = []
    document_content = preprocessed_documents[document_id]
    if isinstance(positions, int):  # Handle the case when positions is an integer
        positions = [positions]
    for position in positions:
        start = max(position - 25, 0)
        end = min(position + 26, len(document_content))
        paragraph = ' '.join(document_content[start:end])
        paragraphs.append(paragraph)

    return paragraphs




# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')


# Route for handling search requests
# Route for handling search requests
@app.route('/search', methods=['POST'])
def search():
    global index  # Declare the index variable as global

    search_word = request.form['query']

    if search_word in index:
        matching_documents = index[search_word]
        results = []
        for doc_id, positions in matching_documents:
            result = {
                'document_id': doc_id,
                'positions': positions,
                'paragraphs': get_paragraphs(doc_id, positions),  # Add the 'paragraphs' key
                'tokens': preprocessed_documents[doc_id]  # Add the 'tokens' key
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

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Attempt to list the containers in the storage account
    containers = blob_service_client.list_containers()

    # If the containers are listed successfully, it means the storage account is accessible
    print("Storage account is accessible. Containers:")
    for container in containers:
        print(container.name)

    # Preprocess the documents from Azure Blob Storage
    preprocessed_documents = preprocess_documents_from_blob_storage(connection_string, container_name)

    # Build the index
    index = build_index(preprocessed_documents)

    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['DEBUG'] = True

    app.run()
