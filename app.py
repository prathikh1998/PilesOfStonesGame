from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

# Game state variables
players = {}
scores = {}
question = ""
player_responses = {}

@app.route('/')
def index():
    return render_template('judge.html')

@app.route('/player')
def player():
    return render_template('player.html')

@socketio.on('connect')
def handle_connect():
    emit('update_scores', scores)

@socketio.on('join')
def handle_join(player_name):
    players[request.sid] = player_name
    scores[player_name] = 0

@socketio.on('question')
def handle_question(q):
    global question
    question = q
    emit('new_question', q, broadcast=True)

@socketio.on('answer')
def handle_answer(answer):
    player_name = players[request.sid]
    player_responses[player_name] = answer
    emit('response', {'player': player_name, 'answer': answer}, broadcast=True)

@socketio.on('judge_response')
def handle_judge_response(data):
    player_name = data['player']
    response = data['response']
    emit('judge_response', {'player': player_name, 'response': response}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
