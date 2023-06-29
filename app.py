from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        l1 = int(request.form['l1'])
        l2 = int(request.form['l2'])
        iv = request.form['iv']
        return render_template('password.html', l1=l1, l2=l2, iv=iv)
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    password = request.form['password']
    l1 = int(request.form['l1'])
    l2 = int(request.form['l2'])
    iv = request.form['iv']
    result = validate_password(password, l1, l2, iv)
    return render_template('results.html', result=result)

def validate_password(password, l1, l2, iv):
    # Your password validation logic here
    # Return a dictionary with 'valid' and 'reason' keys
    
    # Example implementation
    # You can replace this with your actual password validation logic
    if len(password) < l1 or len(password) > l2:
        return {'valid': False, 'reason': f"Password length should be between {l1} and {l2} characters."}
    elif not any(char.isdigit() for char in password):
        return {'valid': False, 'reason': 'Password must contain at least one digit.'}
    elif len([char for char in password if char.isupper()]) < 2:
        return {'valid': False, 'reason': 'Password must contain at least two uppercase letters.'}
    elif not any(char in '#@+-%' for char in password):
        return {'valid': False, 'reason': 'Password must contain at least one of the characters: #@+-%.'}
    elif any(char in iv for char in password):
        return {'valid': False, 'reason': 'Password cannot contain the characters from the invalid list.'}
    else:
        return {'valid': True, 'reason': None}

if __name__ == '__main__':
    app.run()
