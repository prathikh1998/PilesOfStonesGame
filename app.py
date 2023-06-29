#HERE BOTH ARE SAME app and app2

import os
import re
import string
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from flask import Flask, render_template, request
from azure.storage.blob import BlobServiceClient

# Create a Flask application instance
app = Flask(__name__)

# Global variables for storing the index and preprocessed documents
index = None
preprocessed_documents = None
file_names = None  # Variable to store file names

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

# Function to preprocess documents from Azure Blob Storage
def preprocess_documents_from_blob_storage(connection_string, container_name):
    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    preprocessed_docs = []
    file_names = []  # List to store file names

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
        file_names.append(blob.name)  # Store the file name

    print(preprocessed_docs)
    print(file_names)

    return preprocessed_docs, file_names

# Function to build the index
def build_index(preprocessed_docs):
    index = {}
    for doc_id, doc in enumerate(preprocessed_docs):
        for position, word in enumerate(doc):
            if word in index:
                index[word].append((doc_id, position))
            else:
                index[word] = [(doc_id, position)]
    return index

# Function to search for combinations of words in close proximity
def search_combinations(index, search_words, proximity):
    matching_documents = []
    if all(word in index for word in search_words):
        positions = [index[word] for word in search_words]
        for doc_id, positions_1 in positions[0]:
            if isinstance(positions_1, int):  # Handle case where positions_1 is an integer
                positions_1 = [positions_1]
            for position_1 in positions_1:
                found = True
                for i in range(1, len(positions)):
                    found_match = False
                    for doc_id_2, positions_2 in positions[i]:
                        if isinstance(positions_2, int):  # Handle case where positions_2 is an integer
                            positions_2 = [positions_2]
                        for position_2 in positions_2:
                            if abs(position_2 - position_1) <= proximity:
                                found_match = True
                                break
                        if found_match:
                            break
                    if not found_match:
                        found = False
                        break
                if found:
                    matching_documents.append((doc_id, position_1))

    return matching_documents

def find_n_most_frequent_words(preprocessed_docs, n):
    word_counts = {}
    for doc in preprocessed_docs:
        for word in doc:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    most_frequent_words = [word for word, count in sorted_words[:n]]

    return most_frequent_words

# Function to get the paragraphs from a document based on positions
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
@app.route('/search', methods=['POST'])
def search():
    global index, preprocessed_documents, file_names

    search_query = request.form['query']
    
    proximity = 2  # Set the proximity value as desired

    # Preprocess the search query
    search_words = preprocess_document(search_query)

    preprocessed_documents, file_names = preprocess_documents_from_blob_storage("DefaultEndpointsProtocol=https;AccountName=sampl;AccountKey=GLijF+wF353BH7/A3FtGIegOfCfSYrMnZMtsTMT1N9euUX0VB7ihhrmbm+VFjZCZWI4lEos+yd/Q+AStwAJVcw==;EndpointSuffix=core.windows.net", "sampl1")

    # Build the index
    index = build_index(preprocessed_documents)

    # Search for combinations
    matching_documents = search_combinations(index, search_words, proximity)

    n = int(request.form['n'])

    # Get the n most frequent words
    most_frequent_words = find_n_most_frequent_words(preprocessed_documents, n)

    # ...existing code...

    results = []
    for doc_id, position in matching_documents:
        result = {
            'file_name': file_names[doc_id],  # Include the file name instead of the doc_id
            'positions': [(doc_id, position)],  # Include both document ID and position
            'paragraphs': get_paragraphs(doc_id, position),
            'tokens': preprocessed_documents[doc_id]
        }
        results.append(result)

    return render_template('results.html', results=results, most_frequent_words=most_frequent_words)

# Run the Flask application
if __name__ == '__main__':
    
    app.run()