'''
A battlesnake AI based on the 2016 battlesnake API. Seeks the closest food on the board.
Avoids head on collisions with other snakes and other risky moves.

Author: Elio Ferri, Lee Zeitz
'''
import sys
import bottle
import os
import random

from board_frame import BoardFrame
from snake_util import closestFood, weightedConeMove, findMove, safe, altMove, avoidSmallSpace


@bottle.route('/')
def static():
	return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
	return bottle.static_file(path, root='static/')


@bottle.post("/start")
@bottle.post("//start")
def start():
	data = bottle.request.json

	return {
		"color": "#C42B3A",
		"name": "codesnake",
		"headType": "sand-worm",
		"tailType": "fat-rattle"
	}


@bottle.post("/move")
def move():

	data = bottle.request.json

	board = BoardFrame(data)

	if board.ourLoc is None:
		return {
			"move": "up"
		}

	if board.foods:
		dest = closestFood(board)
	else:
		if (board.ourLoc == [board.width-1,board.height-1]):
			dest = [0,0]
		else:
			dest = [board.width-1,board.height-1]

	if (board.ourSnake['health'] > 25):
		if board.ourSnake['health'] > 55:
			coneMove = weightedConeMove(board, False)
		
		else:
			# Go towards the closest food, otherwise go towards a corner of the board. 
			coneMove = weightedConeMove(board, True)
		
		spaceMove = avoidSmallSpace(board)

		# Check if we are putting ourselves in a hole with less moves than our length, and that coneMove is safe
		if (spaceMove[1][1] < board.ourSnake['length']*6 or not safe(board, coneMove)):
			move = spaceMove[0][0]
			whichMove = "space"
		else:
			move = coneMove
			whichMove = "cone"

	else:
		move = findMove(board, dest)
		whichMove = "backup"
		
	# Find altrenate safe move if the desired move was not ideal.
	# TODO: maybe should be a while loop? Call alt move until it's actually ideal?
	if not safe(board, move):
		move = altMove(board, move, dest)
		whichMove = "alt"
		print("alt")

	# Catch errors and display in taunt to debug.
	if move == "no_safe":
		print ("ERROR!")
		return{
			"move": "up",
		}

	else:
		return {
			"move": move,
		}


@bottle.post("/end")
def end():
	data = bottle.request.json

	return {
		"message": "dang"
	}

@bottle.post("/ping")
def ping():
	data = bottle.request.json

	return {
		"message": "still alive"
	}

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
	if len(sys.argv) > 1:
		port = sys.argv[1]
	else:
		port = 8080

	bottle.run(
		application,
		host=os.getenv('IP', '0.0.0.0'),
		port=os.getenv('PORT', port),
		server="gunicorn")
