from flask import Flask, render_template, request, redirect
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
games = {}


class NimGame:
    def __init__(self, num_piles, num_stones):
        self.num_piles = num_piles
        self.piles = [num_stones] * num_piles
        self.current_player = None

    def start_game(self):
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
    num_piles = 3  # Fixed number of piles
    num_stones = 5  # Fixed number of stones in each pile

    game_id = generate_game_id()
    game = NimGame(num_piles, num_stones)
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


def generate_game_id():
    return str(random.randint(1000, 9999))


if __name__ == '__main__':
    app.run(debug=True)
