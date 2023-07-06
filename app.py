from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

# Game state variables
players = {}
scores = {}
question = ""

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
    if answer == question:
        scores[player_name] += 1
        emit('judgment', {'answer': answer, 'correct': True})
        emit('end_game', broadcast=True)
    else:
        scores[player_name] -= 2
        emit('judgment', {'answer': answer, 'correct': False})

if __name__ == '__main__':
    socketio.run(app)
