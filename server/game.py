from scraper import *
from words import *


class Player():
    def __init__(self, name, socket):
        self.name = name
        self.socket = socket


class Game():
    def __init__(self):
        self.url = None
        self.word = None
        self.starting_in = 45
        # possible states: preround, guessing, postround
        self.state = "preround"
        self.round_winner = None
        self.lives = 3
        self.max_round_time = 30
        self.round_time = self.max_round_time
        self.score = 0
        self.player_scores = {}

    def reset_timer(self):
        self.round_time = self.max_round_time

    def new_word(self, dlp, dlurl):
        word = get_random_word()
        url = scrape_word(word, dlp, dlurl)
        if(url == None or url == "" or word == None or word == ""):
            print("Scrape returned null!")
            self.new_word()
        self.word = word
        self.url = url

    def jsonScores(self):
        data = {}
        scores = []
        for player in self.player_scores:
            data[player.name] = self.player_scores[player]
        srt = dict(
            sorted(data.items(), key=lambda item: item[1], reverse=True))
        for x in srt.keys():
            scores.append({"player": x, "score": srt[x]})
        return scores

    def add_one_score(self, player):
        for p2 in self.player_scores.keys():
            if player.name == p2.name:
                self.player_scores[p2] += 1
                return
        self.player_scores[player] = 1

    def check_guess(self, player, guess):
        if guess.lower() == self.word:
            self.state = "postround"
            self.round_winner = player
            self.add_one_score(player)
            return True
        return False

    def hint(self):
        words = self.word.split(" ")
        hint_words = [word[0] + (len(word)-1)*"_" for word in words]
        return " ".join(hint_words).upper()


class Lobby():
    def __init__(self):
        self.players = set()
        # possible states: waiting, starting, playing, finishing
        self.state = "waiting"

    async def send_all(self, msg):
        for player in self.players:
            await player.socket.send(msg)

    def add_player(self, name, socket):
        p = Player(name, socket)
        self.players.add(p)
        return p

    def remove_player(self, name):
        for player in self.players:
            if player.name == name:
                self.players.remove(player)
                break

    def has_player(self, name):
        for player in self.players:
            if player.name == name:
                return True
        return False

    def player_list(self):
        return sorted([p.name for p in self.players])
