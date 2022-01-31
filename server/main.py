from scraper import *
from words import *
from game import *

import json
import asyncio
import datetime
import random
import websockets
import argparse
import ssl

game = None
lobby = Lobby()

start_task = None
round_task = None
logging = True

parser = argparse.ArgumentParser()
parser.add_argument("address")
parser.add_argument("port", type=int)
parser.add_argument("dlp")
parser.add_argument("dlurl")
parser.add_argument("--ssl", nargs=2)

args = parser.parse_args()


def log(msg):
    if logging:
        print(msg)


def packet(status, **kwargs):
    data = {"status": status}
    for v in kwargs:
        data[v] = kwargs[v]
    return json.dumps(data)


async def start_round():
    global game, round_task, start_task, args
    game.state = "preround"
    await lobby.send_all(packet(status="STARTING_ROUND"))
    game.state = "guessing"
    await lobby.send_all(packet(status="NEW_ROUND", img_url=game.url))
    game.reset_timer()
    while game.round_time > 0:
        await lobby.send_all(packet(status="ROUND_TIME_LEFT", time_left=game.round_time))
        if game.round_time == int(game.max_round_time / 3):
            await lobby.send_all(packet(status="HINT", data=game.hint()))
        await asyncio.sleep(1)
        game.round_time -= 1
    game.state = "postround"
    game.lives -= 1
    await lobby.send_all(packet(status="ROUND_FAILED", word=game.word, lives=game.lives))
    if game.lives == 0:
        await lobby.send_all(packet(status="GAME_OVER", scores=game.jsonScores(), team_score=game.score))
    game.new_word(args.dlp, args.dlurl)
    if game.lives > 0:
        await asyncio.sleep(5)
        round_task = asyncio.create_task(start_round())
    else:
        # Game over
        lobby.state = "finishing"
        # Send final scores and winner
        await asyncio.sleep(12)
        lobby.state = "waiting"
        game = None
        if len(lobby.players) > 0:
            start_task = asyncio.create_task(start_game())


async def next_round():
    global round_task, args
    game.new_word(args.dlp, args.dlurl)
    await asyncio.sleep(5)
    round_task = asyncio.create_task(
        start_round())


async def start_game():
    global game, round_task, args
    lobby.state = "starting"
    await lobby.send_all(packet(status="STARTING_GAME"))
    game = Game()
    game.new_word(args.dlp, args.dlurl)
    while game.starting_in > 0:
        await lobby.send_all(packet(status="STARTING_SOON", starting_in=game.starting_in))
        await asyncio.sleep(1)
        game.starting_in -= 1
    await lobby.send_all(packet(status="STARTING"))
    lobby.state = "playing"
    log("Game starting now!")
    round_task = asyncio.create_task(start_round())


async def time(socket, path):
    global start_task, round_task, game
    name = await socket.recv()
    while lobby.has_player(name):
        await socket.send(packet(status="JOIN_FAILED", details=f"The name {name} is already taken!"))
        name = await socket.recv()
    player = lobby.add_player(name, socket)
    log(f"Player joined: {name}")
    await socket.send(packet(status="JOIN_SUCCESS"))
    await lobby.send_all(packet(status="PLAYER_LIST", players=lobby.player_list()))
    if lobby.state == "playing":
        await socket.send(packet(status="IN_GAME", scores=game.jsonScores()))
        if game.state == "guessing":
            await socket.send(packet(status="NEW_ROUND", img_url=game.url))
        elif game.state == "postround":
            await socket.send(packet(status="POST_ROUND"))
    elif lobby.state == "finishing":
        await socket.send(packet(status="IN_GAME", scores=game.jsonScores()))
        await socket.send(packet(status="GAME_OVER", scores=game.jsonScores(), team_score=game.score))
    try:
        if lobby.state == "waiting":
            log("Game will start soon")
            start_task = asyncio.create_task(start_game())

        msg = None
        while True:
            if msg == None:
                msg = await socket.recv()
            elif msg == "":
                continue
            elif msg[0] == "/":
                # handle command
                pass
            else:
                # handle message or guess
                if lobby.state == "waiting" or lobby.state == "starting" or lobby.state == "finishing":
                    await lobby.send_all(packet(status="MESSAGE", player=name, data=msg))
                elif lobby.state == "playing":
                    if game.state == "guessing":
                        # Check guess
                        if game.check_guess(player, msg):
                            # Guess was correct
                            round_task.cancel()
                            game.score += 1
                            await lobby.send_all(packet(status="GUESS", player=name, data=msg))
                            await lobby.send_all(packet(status="ROUND_PASSED", player=name, data=msg, scores=game.jsonScores(), new_score=game.score))
                            asyncio.create_task(next_round())
                        else:
                            await lobby.send_all(packet(status="GUESS", player=name, data=msg))
                    else:
                        await lobby.send_all(packet(status="MESSAGE", player=name, data=msg))
            msg = await socket.recv()
    finally:
        if lobby.has_player(name):
            lobby.remove_player(name)
            log(f"Player left: {name}")
        if (lobby.state == "starting" or lobby.state == "finishing") and len(lobby.players) == 0:
            log("Reset lobby to waiting state")
            if start_task != None:
                start_task.cancel()
                start_task = None
            lobby.state = "waiting"
        if lobby.state == "playing" and len(lobby.players) == 0:
            log("Reset lobby to waiting state")
            if round_task != None:
                round_task.cancel()
                round_task = None
            game = None
            lobby.state = "waiting"
        await lobby.send_all(packet(status="PLAYER_LIST", players=lobby.player_list()))

if args.ssl != None:
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(args.ssl[0], args.ssl[1])
    start_server = websockets.serve(
        time, args.address, args.port, ssl=ssl_context)
else:
    start_server = websockets.serve(time, args.address, args.port)

print("Starting server!")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
