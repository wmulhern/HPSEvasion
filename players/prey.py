#imports

import socket
import random
import sys
import time
import random
import math

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
hunter_vel = [1,1]
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


def euclideanDistance(x1, y1, x2, y2):
    distance = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)
    return math.sqrt(distance)



# PREY LOGIC #
'''
if num walls == 0
    if hunter is moving away
        follow them
        aim for behind them shifted off thier trajectory by euclidian distance of 4
            which ever side is closer
    elif hunter is moving toward us:
        go towards them, more than distance 4 off thier trajectory
    what if at corner?
TODO handle corners
	stop if near corner (< 10), keep going if near wall


TODO: explore with walls
Hunter behavior changes after they hit one of their walls
elif num walls >= 0:
    AHHHHHHHHH
    do same until trapped between walls with small distance
    then run away!
    what if not in same section as hunter? get into a far corner??


HUNTER OPTIONS
once the first wall is created
	only trap in front
	trap from behind in pipe
	trap from behind into rectange
they will likely stick with trap in front or trap behind in rect
	** No one smart should trap behind in rectangle
Define pipe, in diff section than hunter
If in pipe and hunter not
	want to be next to edge closest to hunter to not trap smaller
	in line with hunter, slightly behind in other direction (same logic as before...)
Calculate where hunter will re-enter pipe
	stop at safe distance from that
As soon as they are inside of pipe
	PIPE LOGIC

PIPE LOGIC
see if can get to other side of pipe without being caught
if cant, run away

'''

# PREY FUNCTIONS #
def follow_hunter():
	global hunter_loc
	global hunter_vel
	global prey_loc
	result = [0, 0]

	neg = (sum(hunter_vel) == 0)
	if neg: #neg slope
		path = [[x+3 for x in hunter_loc], [x-3 for x in hunter_loc]]
	else:
		path = [[hunter_loc[0]+3, hunter_loc[1]-3],[hunter_loc[0]-3, hunter_loc[1]+3]]
	dists =[ euclideanDistance(x[0], x[1], *prey_loc) for x in path ] 
	nearest_path = path[dists.index(min(dists))]
	aim_point = nearest_point_on_line(nearest_path[0], nearest_path[1], neg, *prey_loc)
	if aim_point == prey_loc:
		aim_point = nearest_path
	if aim_point[0] < prey_loc[0]:
		result[0] = -1
	elif aim_point[0] > prey_loc[0]:
		result[0] = 1
	if aim_point[1] < prey_loc[1]:
		result[1] = -1
	elif aim_point[1] > prey_loc[1]:
		result[1] = 1
return result


#def hunter_hit_pipe():
	


def detect_pipe():
	global hunter_loc
	up, down, left, right = get_corners()
	if 	hunter_loc[0] < left or hunter_loc[0] > right or \
		hunter_loc[1] < down or hunter_loc[1] > up:
		return True
	else:
		return False

def get_corners():
	global prey_loc
	global wall_locaitons
	left = 0
	right = 299
	up = 299
	down = 0
	for wall in wall_locations:
		if wall[0] == 0: # horizontal wall
			if wall[1] > prey_loc[1] and wall[1] < up:
				up = wall[1]
			if wall[1] < prey_loc[1] and wall[1] > down:
				down = wall[1]
		else :  # vertical wall
			if wall[1] > prey_loc[1] and wall[1] < left:
				left = wall[1]
			if wall[1] < prey_loc[1] and wall[1] > right:
				right = wall[1]
	return [up, down, left, right]


def near_wall():
	global prey_loc
	global hunter_loc
	global hunter_vel
	up, down, left, right = get_corners()
	if euclideanDistance(prey_loc[0], prey_loc[1], hunter_loc[0], hunter_loc[1]) <= 6:
		if 	(hunter_vel[0] == 1 and math.abs(right - prey[0]) <= 6) or / 
		 	(hunter_vel[0] == -1 and math.abs(prey[0] - left) <= 6) or / 
		 	(hunter_vel[1] == 1 and math.abs(up - prey[0]) <= 6) or / 
		 	(hunter_vel[1] == -1 and math.abs(prey[0] - down) <= 6):
			return True
	return False


def near_corner():
	global prey_loc
	global wall_locations
	left = 0
	right = 299
	up = 299
	down = 0
	
	if len(wall_locations) != 0:
		up, down, left, right = get_corners()
	if  (prey_loc[0] >= right - 10 and prey_loc[1] >= up - 10) :
		return True, -1, -1
	if 	(prey_loc[0] >= right - 10 and prey_loc[1] <= down + 10):
		return True, -1, 1
	if 	(prey_loc[0] <= left + 10 and prey_loc[1] >= up - 10):
		return True, 1, -1
	if 	(prey_loc[0] <= left + 10 and prey_loc[1] <= down + 10):
		return True, 1, 1
	else:
		return False, 0, 0

			


# dir, neg = True, pos = False
def nearest_point_on_line(x, y, direction, target_x, target_y):
	min_dist = euclideanDistance(x, y, target_x, target_y)
	if direction:
		move = [-1, 1]
	else:
		move = [1, 1]
	new_x = x + move[0]
	new_y = y + move[1]
	if euclideanDistance(new_x, new_y, target_x, target_y) > min_dist:
		move = [n*(-1) for n in move]
	new_x = x + move[0]
	new_y = y + move[1]
	tmp = euclideanDistance(x+move[0], y+move[1], target_x, target_y)
	while tmp < min_dist:
		min_dist = tmp
		x = x + move[0]
		y = y + move[1]
		tmp = euclideanDistance(x+move[0], y+move[1], target_x, target_y)
	return [x, y]




while True:
	wall_locations = []
	data = sock.recv(4096)
	lines = data.split("\n")
	if len(lines) == 0:
		continue
	line = lines[-2]

	print "recieved:", line
	if line == "done":
		break
	elif line == "hunter":
		hunter_flag = True
		prey_flag = not hunter_flag
		continue
	elif line == "prey":
		hit_wall = False
		in_pipe = False
		prey_flag = True
		hunter_flag = not prey_flag
		continue
	elif line == "sendname":
		result_to_send = "NoEscape"
	else:
		#we received game state
		recent_data = map(int,line.split()) #get the last line from the socket
		initial_info = recent_data[:15] #inputs up until the wall info
		tick_num = initial_info[2]
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
			# check game state
			move = [0, 0]
			if not hit_wall and hunter_loc[0] != hunter_loc[1]:
				hit_wall = True
			if not in_pipe and detect_pipe() == True:
				in_pipe == True

			#check if the prey can move during this tick
			preymove = tick_num % 2 != 0 
			if not preymove:
				if prey_flag:
					#if we are the prey, and we can't move, skip this. Could do computation here later
					result = [game_num, tick_num, 0, 0]
			# we can move...do something
			else:
				if not in_pipe:
					# if near corner, go the other way
					corner, move[0], move[1] = near_corner()
					if corner == False:
						if near_wall() == False:
							# just follow the hunter at a safe distance
							move = follow_hunter()
				else:
					# We are in a pipe
					move[0] = 1 #movement in x direction
					move[1] = 1 #movement in y direction
				result = [game_num,tick_num,move[0], move[1]]
			# for debugging
			time.sleep(.1)


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
		result_to_send = ' '.join(map(str,result)) #convert results to strings so socket can read
	print "sending:", result_to_send
	sock.sendall(result_to_send + "\n") #send to socket
sock.close()

