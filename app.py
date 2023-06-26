import os
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from flask import Flask, render_template, request

nltk.download('stopwords')

# Create a Flask application instance
app = Flask(__name__)

# Declare the global variable for the index
index = {}

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
def preprocess_documents_from_folder(directory):
    preprocessed_docs = []

    # Iterate over the files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            print(f"Processing file: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as file:
                document_content = file.read()
                tokens = preprocess_document(document_content)
                preprocessed_docs.append(tokens)

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
    global index  # Declare the index variable as global

    search_word = request.form['query']

    if search_word in index:
        matching_documents = index[search_word]
        results = []
        for doc_id, position in matching_documents:
            result = {
                'document_id': doc_id,
                'position': position,
                'tokens': preprocessed_documents[doc_id]  # Add the 'tokens' key
            }
            results.append(result)
    else:
        results = []

    return render_template('results.html', results=results)



# Run the Flask application
if __name__ == '__main__':
    # Directory where the documents are stored
    documents_directory = 'presidential_databases'

    # Preprocess the documents from the folder
    preprocessed_documents = preprocess_documents_from_folder(documents_directory)

    # Build the index
    index = build_index(preprocessed_documents)

    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['DEBUG'] = True

    app.run()
