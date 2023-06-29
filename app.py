#HERE BOTH ARE SAME app and app2
#HERE THE FREQUENCY AND THE MATCHING DOCS ARE PRINTED

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
    #document = document.lower()

    # Remove punctuation marks
    document = document.translate(str.maketrans("", "", string.punctuation))

    # Split the text into individual words or tokens
    tokens = document.split()

    # Remove stop words
    stop_words = set(stopwords.words("english"))
    tokens = [token for token in tokens if token not in stop_words]

    # Word stemming (optional)
    #stemmer = PorterStemmer()
    #tokens = [stemmer.stem(token) for token in tokens]

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

def find_most_frequent_words(index, n):
    word_frequencies = {}
    for word, positions in index.items():
        word_frequencies[word] = len(positions)
    sorted_words = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:n]

def get_paragraphs_from_blob_storage(file_name, word):
    # Connect to your Azure storage account
    connection_string = 'DefaultEndpointsProtocol=https;AccountName=sampl;AccountKey=GLijF+wF353BH7/A3FtGIegOfCfSYrMnZMtsTMT1N9euUX0VB7ihhrmbm+VFjZCZWI4lEos+yd/Q+AStwAJVcw==;EndpointSuffix=core.windows.net'
    container_name = 'sampl1'

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    blob_client = container_client.get_blob_client(file_name)
    file_content = blob_client.download_blob().readall().decode('utf-8')
    paragraphs = file_content.split('\n\n')

    matching_paragraphs = []
    for paragraph in paragraphs:
        if word in paragraph:
            matching_paragraphs.append(paragraph)

    return matching_paragraphs



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
    most_frequent_words = find_most_frequent_words(index, n)  # Fix the function name

    results = []
    for doc_id, position in matching_documents:
        result = {
            'file_name': file_names[doc_id],
            'positions': [(doc_id, position)],
            'paragraphs': get_paragraphs_from_blob_storage(file_names[doc_id], search_query),
            'tokens': preprocessed_documents[doc_id]
        }
        results.append(result)


    return render_template('results.html', results=results, most_frequent_words=most_frequent_words)




@app.route('/search_lines', methods=['POST'])
def search_lines():
    word = request.form.get('word')
    n = int(request.form.get('n'))
    matching_lines = []

    # Connect to your Azure storage account
    connection_string = 'DefaultEndpointsProtocol=https;AccountName=sampl;AccountKey=GLijF+wF353BH7/A3FtGIegOfCfSYrMnZMtsTMT1N9euUX0VB7ihhrmbm+VFjZCZWI4lEos+yd/Q+AStwAJVcw==;EndpointSuffix=core.windows.net'
    container_name = 'sampl1'

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    filenames = ['1960-09-26.txt', '1960-10-07.txt']

    for filename in filenames:
        blob_client = container_client.get_blob_client(filename)
        file_contents = blob_client.download_blob().readall().decode('utf-8')
        
        lines = file_contents.split('\n')
        for line in lines:
            if word in line:
                matching_lines.append(line)
                if len(matching_lines) == n:
                    break
        if len(matching_lines) == n:
            break

    # Extract the first 'n' sentences where the word 'president' is mentioned
    sentences = []
    for line in matching_lines:
        sentences.extend(re.split(r'(?<=[.!?])\s+', line))
    
    matching_sentences = [sentence for sentence in sentences if 'president' in sentence.lower()][:n]

    return render_template('line.html', matching_sentences=matching_sentences)



if __name__ == '__main__':
    app.run()