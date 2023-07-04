from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import redis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

# Initialize game state
redis_host = 'ass6cache.redis.cache.windows.net'
redis_port = 6379
redis_password = 'ugMdQa89swtNhUNPnXsoXNwqzjv4WWDYqAzCaPwhKNA='
GAME_STATE_KEY = "game_state"
DEFAULT_PILES = [5, 4, 3]
DEFAULT_PLAYERS = ['Player 1', 'Player 2']

def get_game_state():
    r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
    state = r.get(GAME_STATE_KEY)
    if state is None:
        # Initialize game state if it doesn't exist in Redis
        state = {
            'players': DEFAULT_PLAYERS,
            'scores': [0, 0],
            'piles': DEFAULT_PILES,
            'active_player': 0
        }
        r.set(GAME_STATE_KEY, str(state))
    else:
        state = eval(state.decode('utf-8'))  # Convert bytes to dictionary
    return state

def update_game_state(state):
    r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
    r.set(GAME_STATE_KEY, str(state))

@app.route('/')
def home():
    game_state = get_game_state()
    return render_template('game.html', game_state=game_state)

@socketio.on('start_game')
def handle_start_game(data):
    game_state = get_game_state()
    game_state['players'] = [data['player1'], data['player2']]
    game_state['scores'] = [0, 0]
    game_state['piles'] = data['piles']
    game_state['active_player'] = data['active_player']
    update_game_state(game_state)
    emit('game_started', {'game_state': game_state}, broadcast=True)

@socketio.on('make_move')
def handle_make_move(data):
    game_state = get_game_state()
    move = int(data['move'])
    stones = int(data['stones'])
    active_player = game_state['active_player']
    game_state['piles'][move] -= stones
    game_state['scores'][active_player] += stones
    game_state['active_player'] = 1 - active_player  # Toggle active player
    update_game_state(game_state)

    # Check if all piles have 0 stones
    if all(stones == 0 for stones in game_state['piles']):
        # Declare the winner
        winner_index = game_state['scores'].index(max(game_state['scores']))
        game_state['winner'] = game_state['players'][winner_index]
        emit('winner_declared', {'game_state': game_state}, broadcast=True)
    else:
        emit('move_made', {'game_state': game_state}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
