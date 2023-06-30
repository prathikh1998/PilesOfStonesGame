from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from multiprocessing import Process, Manager
from redis import Redis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)
redis = Redis()

class Game:
    def __init__(self, pile1, pile2, pile3, min_pickup, max_pickup, player1, player2):
        self.piles = [pile1, pile2, pile3]
        self.min_pickup = min_pickup
        self.max_pickup = max_pickup
        self.players = [player1, player2]
        self.current_player = 0
        self.scores = [0, 0]

    def take_turn(self, pile_index, stones_taken):
        pile = self.piles[pile_index]
        if stones_taken < self.min_pickup or stones_taken > self.max_pickup or pile < stones_taken:
            return False

        pile -= stones_taken
        self.piles[pile_index] = pile
        self.scores[self.current_player] += stones_taken

        self.current_player = (self.current_player + 1) % 2
        return True

    def is_game_over(self):
        return all(pile == 0 for pile in self.piles)

    def get_winner(self):
        if self.scores[0] > self.scores[1]:
            return self.players[0]
        elif self.scores[1] > self.scores[0]:
            return self.players[1]
        else:
            return "It's a tie!"

games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_game():
    pile1 = int(request.form['pile1'])
    pile2 = int(request.form['pile2'])
    pile3 = int(request.form['pile3'])
    min_pickup = int(request.form['min_pickup'])
    max_pickup = int(request.form['max_pickup'])
    player1 = request.form['player1']
    player2 = request.form['player2']

    game = Game(pile1, pile2, pile3, min_pickup, max_pickup, player1, player2)
    game_id = len(games) + 1
    games[game_id] = game

    socketio.emit('new_game', {'game_id': game_id, 'game': game}, broadcast=True)

    return ''

@app.route('/play', methods=['POST'])
def play():
    game_id = int(request.form['game_id'])
    pile_index = int(request.form['pile_index'])
    stones_taken = int(request.form['stones_taken'])

    game = games[game_id]
    success = game.take_turn(pile_index, stones_taken)

    if game.is_game_over():
        winner = game.get_winner()
        del games[game_id]
        socketio.emit('game_over', {'winner': winner}, broadcast=True)
    else:
        socketio.emit('game_update', {'game_id': game_id, 'game': game, 'success': success}, broadcast=True)

    return ''

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
