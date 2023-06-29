from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text_input = request.form['text_input']
        word = request.form['word']
        words = request.form['words']
        modified_text = modify_text(text_input, word, words)
        return render_template('results.html', modified_text=modified_text)
    return render_template('index.html')

def modify_text(text_input, word, words):
    modified_text = text_input

    if word:
        modified_text = remove_word(modified_text, word)

    if words:
        modified_text = find_words(modified_text, words)

    return modified_text

def remove_word(text, word):
    return text.replace(word, '')

def find_words(text, words):
    w1, w2 = words.split()

    occurrences = []
    index = 0

    while index < len(text):
        found_index = text.find(w1, index)
        if found_index == -1:
            break

        next_index = found_index + len(w1)
        if next_index < len(text) and text[next_index] == ' ':
            next_index += 1

        if text[next_index:].startswith(w2):
            occurrences.append((found_index, found_index + len(w1) + len(w2)))

        index = next_index

    for start, end in reversed(occurrences):
        text = text[:start] + text[end:]

    return text

if __name__ == '__main__':
    app.run()
