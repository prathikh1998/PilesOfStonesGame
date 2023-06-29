from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-password', methods=['POST'])
def check_password():
    # Get the form data from the request
    data = request.get_json()

    # Extract the password and validation criteria
    password = data['password']
    min_length = int(data['minLength'])
    max_length = int(data['maxLength'])
    invalid_chars = data['invalidChars']

    # Perform the password validity check
    if not is_valid_password(password, min_length, max_length, invalid_chars):
        result = {'valid': False, 'reason': 'Password is not valid.'}
    else:
        result = {'valid': True}

    # Render the result.html template with the result data
    return render_template('results.html', result=result)

def is_valid_password(password, min_length, max_length, invalid_chars):
    # Check password length
    if len(password) < min_length or len(password) > max_length:
        return False

    # Check for at least one number
    if not any(char.isdigit() for char in password):
        return False

    # Check for at least two uppercase letters
    if sum(char.isupper() for char in password) < 2:
        return False

    # Check for invalid characters
    if any(char in password for char in invalid_chars):
        return False

    # Additional checks if needed...

    return True

if __name__ == '__main__':
    app.run()
