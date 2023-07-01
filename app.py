from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

games = {}


class NimGame:
    def __init__(self, num_piles):
        self.num_piles = num_piles
        self.piles = []
        self.current_player = None

    def start_game(self):
        self.piles = [5] * self.num_piles
        self.current_player = "Player 1"  # Always start with Player 1

    def take_stones(self, pile_index, num_stones):
        if pile_index < 0 or pile_index >= self.num_piles:
            return False
        if num_stones < 1 or num_stones > self.piles[pile_index]:
            return False

        self.piles[pile_index] -= num_stones

        # Switch to the other player
        if self.current_player == "Player 1":
            self.current_player = "Player 2"
        else:
            self.current_player = "Player 1"

        return True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/game', methods=['POST'])
def new_game():
    player_name = request.form.get('player_name')
    num_piles = int(request.form.get('num_piles'))

    game_id = generate_game_id()
    game = NimGame(num_piles)
    game.start_game()

    games[game_id] = {
        'game': game,
        'player1': player_name,
        'player2': None
    }

    return redirect('/game/' + game_id)


@app.route('/game/<game_id>')
def game(game_id):
    if game_id not in games:
        return "Game not found."

    game_data = games[game_id]
    game = game_data['game']
    player_name = game_data['player1'] if game_data['player1'] else game_data['player2']

    return render_template('game.html', game_id=game_id, game=game, player_name=player_name)


@socketio.on('connect')
def handle_connect():
    room = request.args.get('game_id')
    join_room(room)


@socketio.on('join')
def handle_join(data):
    game_id = data['game_id']
    player_name = data['player_name']

    if game_id in games:
        game_data = games[game_id]
        if not game_data['player1']:
            game_data['player1'] = player_name
        elif not game_data['player2']:
            game_data['player2'] = player_name
        else:
            emit('full_game')
            return

        join_room(game_id)
        emit('game_joined', {'player_name': player_name}, room=game_id)


@socketio.on('take_stones')
def handle_take_stones(data):
    game_id = data['game_id']
    player_name = data['player_name']
    pile_index = data['pile_index']
    num_stones = data['num_stones']

    if game_id in games:
        game_data = games[game_id]
        game = game_data['game']
        current_player = game.current_player

        if player_name == current_player:
            success = game.take_stones(pile_index, num_stones)
            if success:
                emit('update_game', {'game': game.__dict__}, room=game_id)
                if check_game_over(game):
                    winner = get_winner(game, game_data)
                    emit('game_over', {'winner': winner}, room=game_id)
            else:
                emit('invalid_move', room=game_id)
        else:
            emit('not_your_turn', room=game_id)


def generate_game_id():
    return str(random.randint(1000, 9999))


def check_game_over(game):
    return all(pile == 0 for pile in game.piles)


def get_winner(game, game_data):
    if game.current_player == "Player 1":
        return game_data['player2']
    else:
        return game_data['player1']


if __name__ == '__main__':
    socketio.run(app, debug=True)
