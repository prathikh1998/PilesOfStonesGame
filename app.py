import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import redis

class Player:
    def __init__(self, name, score):
        self.name = name
        self.score = score

class Judge:
    def __init__(self, player1, player2, max_attempts, initial_score):
        self.player1 = player1
        self.player2 = player2
        self.max_attempts = max_attempts
        self.initial_score = initial_score
        self.question_log = []
        self.start_time = 0

    def start_game(self):
        self.player1.score = self.initial_score
        self.player2.score = self.initial_score
        self.question_log = []
        self.start_time = time.time()

    def log_question(self, sender, question):
        current_time = time.time() - self.start_time
        self.question_log.append(f'[{current_time:.2f}, {sender.name}] {question}')

    def log_response(self, sender, response, is_correct):
        current_time = time.time() - self.start_time
        self.question_log.append(f'[{current_time:.2f}, {sender.name}] {response}')
        if is_correct:
            self.question_log.append(f'[{current_time:.2f}, Judge] OK')
        else:
            self.question_log.append(f'[{current_time:.2f}, Judge] NO')

    def send_question(self, question):
        self.log_question(self.player1, question)
        self.log_question(self.player2, question)

    def judge_response(self, player, response):
        if self.player1.score <= 0 or self.player2.score <= 0:
            return

        self.log_response(player, response, False)

        if self.player1.score == self.player2.score == self.initial_score:
            self.log_response(self.player1, response, True)
            self.player1.score += 1
        elif player == self.player1:
            if self.player2.score > 0:
                self.log_response(self.player2, response, True)
                self.player2.score += 1
        elif player == self.player2:
            if self.player1.score > 0:
                self.log_response(self.player1, response, True)
                self.player1.score += 1

        self.player1.score -= 2
        self.player2.score -= 2

        if self.player1.score <= 0 or self.player2.score <= 0:
            self.end_game()

    def end_game(self):
        self.question_log.append('Game Over')

# Example usage:
player1 = Player('P1', 5)
player2 = Player('P2', 5)
judge = Judge(player1, player2, max_attempts=4, initial_score=5)

judge.start_game()
judge.send_question('When was the war of 1812?')

# Simulating player responses
judge.judge_response(player1, '1800')
judge.judge_response(player2, '1810')
judge.judge_response(player1, '1812')

# Print the question log
for log_entry in judge.question_log:
    print(log_entry)
