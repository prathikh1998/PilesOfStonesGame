from flask import Flask, render_template, request

app = Flask(__name__)

class Game:
    def __init__(self):
        self.player1 = {'name': 'P1', 'score': 0}
        self.player2 = {'name': 'P2', 'score': 0}
        self.judge = {'name': 'J'}
        self.question_log = []
        self.current_time = 0

    def reset_game(self):
        self.player1['score'] = 0
        self.player2['score'] = 0
        self.question_log = []
        self.current_time = 0

    def add_question_log_entry(self, sender, message):
        entry = {
            'time': self.current_time,
            'sender': sender,
            'message': message
        }
        self.question_log.append(entry)

    def update_scores(self, correct_player, incorrect_player):
        correct_player['score'] += 1
        incorrect_player['score'] -= 2

    def get_current_time(self):
        return self.current_time


game = Game()


@app.route('/')
def index():
    return render_template('game.html', player1=game.player1, player2=game.player2, question_log=game.question_log, current_time=game.get_current_time())


@app.route('/start_game', methods=['POST'])
def start_game():
    game.reset_game()
    return 'Game started!'


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    sender = request.form['sender']
    message = request.form['message']

    if sender == game.player1['name']:
        correct_player = game.player1
        incorrect_player = game.player2
    else:
        correct_player = game.player2
        incorrect_player = game.player1

    game.current_time += 1
    game.add_question_log_entry(sender, message)

    if message.lower() == '1812':
        game.update_scores(correct_player, incorrect_player)
        game.add_question_log_entry(game.judge['name'], 'OK')
    else:
        game.add_question_log_entry(game.judge['name'], 'NO')

    return 'Answer submitted!'


if __name__ == '__main__':
    app.run(debug=True)
