from flask import Flask, render_template, request, redirect
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

games = {}


class NimGame:
    def __init__(self, num_piles):
        self.num_piles = num_piles
        self.piles = []
        self.current_player = None

    def start_game(self):
        self.piles = [10] * self.num_piles
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
    num_piles = request.form.get('num_piles')

    if not num_piles or not num_piles.isdigit():
        return "Invalid number of piles."

    num_piles = int(num_piles)

    game_id = generate_game_id()
    game = NimGame(num_piles)
    game.start_game()

    games[game_id] = {
        'game': game,
        'player1': player_name,
        'player2': None
    }

    return redirect('/game/' + game_id)


# Rest of the code...

if __name__ == '__main__':
    app.run(debug=True)
