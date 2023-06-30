from flask import Flask, render_template, request

app = Flask(__name__)

# Shared data
stone_piles = [0, 0, 0]
players = ['', '']
scores = [0, 0]
turn = 0

# Game configuration
max_stones = 5
min_stones = 1

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_game():
    global stone_piles, players, scores, turn

    stone_piles = [int(request.form['pile1']),
                   int(request.form['pile2']),
                   int(request.form['pile3'])]

    players = [request.form['player1'], request.form['player2']]
    scores = [0, 0]
    turn = 0

    return render_template('game.html', stone_piles=stone_piles, players=players, scores=scores, turn=turn)

@app.route('/play', methods=['POST'])
def play_turn():
    global stone_piles, players, scores, turn

    pile_index = int(request.form['pile_index'])
    stones_taken = int(request.form['stones_taken'])

    if stone_piles[pile_index] == 0:
        error_message = "Cannot take stones from an empty pile."
        return render_template('game.html', stone_piles=stone_piles, players=players, scores=scores, turn=turn, error_message=error_message)

    if stone_piles[pile_index] >= stones_taken:
        stone_piles[pile_index] -= stones_taken
        scores[turn] += stones_taken

    # Check if all stone piles are empty
    if all(pile == 0 for pile in stone_piles):
        winner = players[scores.index(max(scores))]
        return render_template('game_over.html', winner=winner, scores=scores)

    turn = (turn + 1) % 2

    return render_template('game.html', stone_piles=stone_piles, players=players, scores=scores, turn=turn)


if __name__ == '__main__':
    app.run()
