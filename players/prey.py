#imports

import socket
import random
import sys
import time
import random

#set up socket

host = "localhost"
port = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

#initialize variables 

max_walls = None
wall_delay = None
x_size = None
y_size = None
hunter_loc = [0,0]
hunter_velocity = [1,1]
prey_loc = [200,230]
time_until_place_wall = 0
wall_locations = []
num_walls = 0

"""

INPUT DESCRIPTION

0					1		2			3			4						5		6				7				8				9			10
[playerTimeLeft] [gameNum] [tickNum] [maxWalls] [wallPlacementDelay] [boardsizeX] [boardsizeY] [currentWallTimer] [hunterXPos] [hunterYPos] [hunterXVel] 
11				12			13		14			15+
[hunterYVel] [preyXPos] [preyYPos] [numWalls] {wall1 info} {wall2 info} ... 
"""

prey_flag = True
hunter_flag = not prey_flag

while True:
	data = sock.recv(4096)
	lines = data.split("\n")
	if len(lines) == 0: #if no information, keep waiting for socket communication
		continue
	else:
		recent_data = map(int,lines[-1].split()) #get the last line from the socket
	initial_info = recent_data[:15] #inputs up until the wall info
	tick_num = initial_info[2]
	preymove = tick_num % 2 == 0 #check if the prey can move during this tick
	if not preymove:
		if prey_flag:
			#if we are the prey, and we can't move, skip this. Could do computation here later
			continue
	#if static variables haven't been declared, this is first pass through data and declare them
	if max_walls is None:
		max_walls = initial_info[3]
	if wall_delay is None:
		wall_delay = initial_info[4]
	if x_size is None:
		x_size = initial_info[5]
	if y_size is None:
		y_size = initial_info[6]
	#update from rest of the input data
	time_left = initial_info[0]
	game_num = initial_info[1]
	time_until_place_wall = initial_info[7]
	hunter_loc[0] = initial_info[8]
	hunter_loc[1] = initial_info[9]
	hunter_vel[0] = initial_info[10]
	hunter_vel[1] = initial_info[11]
	prey_loc[0] = initial_info[12]
	prey_loc[1] = initial_info[13]
	num_walls = initial_info[14]
	curr_wall_info = []
	#check if there are walls and if there are, update our stored walls
	if num_walls > 0: 
		for i,item in enumerate(lines[15:]):
			curr_wall_info.append(item)
			if (i+1)%4 == 0:
				wall_locations.append(curr_wall_info)
				curr_wall_info = []
	#game logic
	if prey_flag:
		x = 0 #movement in x direction
		y = 0 #movement in y direction
		#----------------------------------#
		#  prey logic (determine x and y)  #
		#----------------------------------#
		result = [game_num,tick_num,x,y]
	if hunter_flag:
		wall_to_add = 0 #type of wall to add. Initialized at no wall. 1 is horizontal and 2 is vertical
		walls_to_delete = [] #list of wall indicies to delete (indicies are from the list of walls created, not the location of the wall on the grid)
		#-----------------------------------------------------------------------#
		#  hunter logic (determine whether to make a wall and/or delete walls)  #
		#-----------------------------------------------------------------------#
		if len(walls_to_delete) == 0:
			result = [game_num,tick_num,wall_to_add]
		else:
			result = [game_num,tick_num,wall_to_add] + walls_to_delete
	result_to_send = map(str,result) #convert results to strings so socket can read
	sock.sendall(" ".join(result_to_send) + "\n") #send to socket
sock.close()

