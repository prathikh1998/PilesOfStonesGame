from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        html_input = request.form['html_input']
        mp_tags, modified_html = extract_mp_tags(html_input)
        return render_template('results.html', mp_tags=mp_tags, modified_html=modified_html)
    return render_template('index.html')

def extract_mp_tags(html_input):
    mp_tags = ['<b>', '</b>', '<i>', '</i>', '<p>', '</p>', '<h1>', '</h1>']
    modified_html = html_input

    stack = []
    mp_tags_occurrences = []

    i = 0
    while i < len(modified_html):
        if modified_html[i:i+2] == '</':
            closing_tag_end = modified_html.find('>', i+2)
            closing_tag = modified_html[i:closing_tag_end+1]

            if stack and stack[-1] == closing_tag[2:]:
                opening_tag_start = modified_html.rfind('<', 0, i)
                opening_tag = modified_html[opening_tag_start:i+1]

                mp_tags_occurrences.append((opening_tag, closing_tag))
                stack.pop()

        elif modified_html[i] == '<':
            opening_tag_end = modified_html.find('>', i+1)
            opening_tag = modified_html[i:opening_tag_end+1]

            if opening_tag in mp_tags:
                stack.append(opening_tag)

        i += 1

    for opening_tag, closing_tag in mp_tags_occurrences:
        modified_html = modified_html.replace(opening_tag, '')
        modified_html = modified_html.replace(closing_tag, '')

    return mp_tags_occurrences, modified_html

if __name__ == '__main__':
    app.run()
