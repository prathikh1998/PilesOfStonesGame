from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Store the game data in session
def get_game_data():
    if 'game_data' not in session:
        # Initialize game data
        session['game_data'] = {
            'player1_stones': 0,
            'player2_stones': 0
        }
    
    if 'player_turn' not in session:
        # Initialize player turn
        session['player_turn'] = 1
    
    return session['game_data']

@app.route('/')
def index():
    game_data = get_game_data()
    return render_template('index.html', game_data=game_data)

@app.route('/play', methods=['POST'])
def play():
    game_data = get_game_data()
    player_move = request.form['move']
    
    if session['player_turn'] == 1:
        game_data['player1_stones'] += int(player_move)
        session['player_turn'] = 2
    else:
        game_data['player2_stones'] += int(player_move)
        session['player_turn'] = 1
    
    return redirect('/')

@app.route('/result')
def result():
    game_data = get_game_data()
    
    if game_data['player1_stones'] > game_data['player2_stones']:
        winner = 'Player 1'
    elif game_data['player1_stones'] < game_data['player2_stones']:
        winner = 'Player 2'
    else:
        winner = 'No one (It\'s a tie!)'
    
    return render_template('game.html', winner=winner)

if __name__ == '__main__':
    app.run()
