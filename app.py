#HERE BOTH ARE SAME app and app2
#HERE THE FREQUENCY AND THE MATCHING DOCS ARE PRINTED and also the sequence and the first lines with words

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

    # Get the stop words from Azure Blob Storage
    connection_string = 'DefaultEndpointsProtocol=https;AccountName=sampl;AccountKey=GLijF+wF353BH7/A3FtGIegOfCfSYrMnZMtsTMT1N9euUX0VB7ihhrmbm+VFjZCZWI4lEos+yd/Q+AStwAJVcw==;EndpointSuffix=core.windows.net'
    container_name = 'sampl2'
    blob_name = 'stopwords.txt'

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    stop_words = set(blob_client.download_blob().readall().decode().splitlines())

    # Remove stop words
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


    return preprocessed_docs, file_names

def find_most_frequent_combinations(preprocessed_docs, n):
    combination_frequencies = {}
    for doc in preprocessed_docs:
        for i in range(len(doc) - 1):
            combination = doc[i] + doc[i + 1]
            if combination in combination_frequencies:
                combination_frequencies[combination] += 1
            else:
                combination_frequencies[combination] = 1
    sorted_combinations = sorted(combination_frequencies.items(), key=lambda x: x[1], reverse=True)
    return sorted_combinations[:n]


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

def get_stop_words(connection_string, container_name):
    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Get the stop words file from the container
    blob_client = container_client.get_blob_client('stopwords.txt')
    stop_words = set(blob_client.download_blob().readall().decode().splitlines())

    return stop_words




@app.route('/search_stop', methods=['POST'])
def search_stop():
    connection_string = 'DefaultEndpointsProtocol=https;AccountName=sampl;AccountKey=GLijF+wF353BH7/A3FtGIegOfCfSYrMnZMtsTMT1N9euUX0VB7ihhrmbm+VFjZCZWI4lEos+yd/Q+AStwAJVcw==;EndpointSuffix=core.windows.net'
    container_name = 'sampl2'

    # Count the occurrence of stop words in the documents
    stop_words = get_stop_words(connection_string, container_name)
    word_count = {}

    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Get the list of file names in the container
    file_names = [blob.name for blob in container_client.list_blobs()]

    for file_name in file_names:
        # Get the blob client for the file
        blob_client = container_client.get_blob_client(file_name)

        # Download and preprocess the document
        document = blob_client.download_blob().readall().decode()
        document_words = preprocess_document(document)

        # Count the occurrence of stop words in the document
        for word in document_words:
            if word in stop_words:
                if word not in word_count:
                    word_count[word] = 0
                word_count[word] += 1

    # Render the template with the word counts
    return render_template('search_results.html', word_count=word_count)



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
    most_frequent_words = find_most_frequent_words(index, n)

    # Get the n most frequent two-letter combinations
    most_frequent_combinations = find_most_frequent_combinations(preprocessed_documents, n)

    results = []
    for doc_id, position in matching_documents:
        result = {
            'file_name': file_names[doc_id],
            'positions': [(doc_id, position)],
            'paragraphs': get_paragraphs_from_blob_storage(file_names[doc_id], search_query),
            'tokens': preprocessed_documents[doc_id]
        }
        results.append(result)

    return render_template('results.html', results=results, most_frequent_words=most_frequent_words, most_frequent_combinations=most_frequent_combinations)


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



def get_lines_from_blob_storage(file_name):
    # Connect to your Azure storage account
    connection_string = 'DefaultEndpointsProtocol=https;AccountName=sampl;AccountKey=GLijF+wF353BH7/A3FtGIegOfCfSYrMnZMtsTMT1N9euUX0VB7ihhrmbm+VFjZCZWI4lEos+yd/Q+AStwAJVcw==;EndpointSuffix=core.windows.net'
    container_name = 'sampl1'

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    blob_client = container_client.get_blob_client(file_name)
    lines = blob_client.download_blob().readall().decode('utf-8').split('\n')

    return lines



@app.route('/replace_and_print', methods=['POST'])
def replace_and_print():
    character = request.form['character']
    replacement = request.form['replacement']

    # Connect to Azure Blob Storage
    connection_string = 'DefaultEndpointsProtocol=https;AccountName=sampl;AccountKey=GLijF+wF353BH7/A3FtGIegOfCfSYrMnZMtsTMT1N9euUX0VB7ihhrmbm+VFjZCZWI4lEos+yd/Q+AStwAJVcw==;EndpointSuffix=core.windows.net'
    container_name = 'sampl1'

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Get the list of file names in the container
    file_names = [blob.name for blob in container_client.list_blobs()]

    # Replace the character in the target documents and get the first 8 sentences from each original document
    modified_documents = []
    for file_name in file_names:
        blob_client = container_client.get_blob_client(file_name)
        document = blob_client.download_blob().readall().decode()
        
        modified_document = []
        original_document = []

        sentence_count = 0
        for line in document.splitlines():
            # Split the line into sentences using regex pattern
            sentences = re.split(r'(?<=[.!?])\s+', line.strip())

            for sentence in sentences:
                # Replace the character in the sentence
                modified_sentence = sentence.replace(character, replacement)
                modified_document.append(modified_sentence)

                # Add the original sentence
                original_document.append(sentence)

                sentence_count += 1
                if sentence_count == 8:
                    break
            
            if sentence_count == 8:
                break
        
        modified_documents.append((modified_document, original_document, file_name))

    return render_template('replace.html', modified_documents=modified_documents)

if __name__ == '__main__':
    app.run()