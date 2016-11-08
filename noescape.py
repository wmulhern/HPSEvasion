#imports

import socket
import random
import sys
import time
import random
import math 

trap_flag = False
alternate_wall_type = 1

#functions
def euclideanDistance(x1, y1, x2, y2):
	distance = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)
	return math.sqrt(distance)

# PREY FUNCTIONS #
def follow_hunter():
	global hunter_loc
	global hunter_vel
	global prey_loc
	result = [0, 0]

	neg = (sum(hunter_vel) == 0)
	if neg: #neg slope
		path = [[x+4 for x in hunter_loc], [x-4 for x in hunter_loc]]
	else:
		path = [[hunter_loc[0]+4, hunter_loc[1]-4],[hunter_loc[0]-4, hunter_loc[1]+4]]
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


def hunter_hit_pipe(direction, wall):
	## TODO: check for other walls
	ticks = None
	global hunter_loc
	global hunter_vel
	global wall_locations
	if direction == "left":
		if hunter_vel[0] == -1:
			# moving away
			ticks = hunter_loc[0] + wall
		else:
			ticks = wall - hunter_loc[0]		
	elif direction == "right":
		if hunter_vel[0] == 1:
			# moving away
			ticks = (300 - hunter_loc[0]) + (300 - wall)
		else:
			ticks = hunter_loc[0] - wall
	
	if ticks != None:
		# y direction
		y_loc = hunter_loc[1] + (hunter_vel[1] * ticks)
		if y_loc < 0 :
			y_loc = abs(y_loc) - 1
		elif y_loc > 299:
			y_loc = 600 - y_loc
		return [wall, y_loc, ticks]

	if direction == "down":
		if hunter_vel[1] == -1:
			# moving away
			ticks = hunter_loc[1] + wall
		else:
			ticks = wall - hunter_loc[1]		
	elif direction == "up":
		if hunter_vel[1] == 1:
			# moving away
			ticks = (300 - hunter_loc[1]) + (300 - wall)
		else:
			ticks = hunter_loc[1] - wall
	
	# x direction
	x_loc = hunter_loc[0] + (hunter_vel[0] * ticks)
	if x_loc < 0 :
		x_loc = abs(x_loc) - 1
	elif x_loc > 299:
		x_loc = 600 - x_loc
	return [x_loc, wall, ticks]
	
def stop_near_hunter(hunter_x, hunter_y, ticks, direction, wall):
	global hunter_vel
	global prey_loc
	if hunter_x == wall:
		x_loc = wall
		up_dist = abs(prey_loc[1] - hunter_y + 6)
		down_dist = abs(prey_loc[1] - hunter_y - 6)
		if hunter_vel[1] == 1 and down_dist < ticks:
			y_loc = hunter_y - 6
		elif hunter_vel[1] == -1 and up_dist < ticks:
			y_loc = hunter_y + 6
		else:
			if down_dist < up_dist:
				y_loc = down_dist
			else:
				y_loc = up_dist
	else:
		y_loc = wall
		right_dist = abs(prey_loc[0] - hunter_x + 6)
		left_dist = abs(prey_loc[0] - hunter_x - 6)
		if hunter_vel[0] == 1 and left_dist < ticks:
			x_loc = hunter_x - 6
		elif hunter_vel[0] == -1 and right_dist < ticks:
			x_loc = hunter_x + 6
		else:
			if left_dist < right_dist:
				x_loc = left_dist
			else:
				x_loc = right_dist
	return [x_loc, y_loc]


def detect_pipe():
	global hunter_loc
	up, down, left, right = get_corners()
	if 	hunter_loc[0] < left:
		return True, "left", left
	elif hunter_loc[0] > right:
		return True, "right", right
	elif hunter_loc[1] < down:
		return True, "down", down
	elif hunter_loc[1] > up:
		return True, "up", up
	else:
		return False, None, None

def get_corners():
	global prey_loc
	global wall_locations
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
			if wall[1] > prey_loc[1] and wall[1] < right:
				right = wall[1]
			if wall[1] < prey_loc[1] and wall[1] > left:
				left = wall[1]
	return [up, down, left, right]


def near_wall():
	global prey_loc
	global hunter_loc
	global hunter_vel
	up, down, left, right = get_corners()
	if euclideanDistance(prey_loc[0], prey_loc[1], hunter_loc[0], hunter_loc[1]) <= 6:
		if 	(hunter_vel[0] == 1 and abs(right - prey_loc[0]) <= 6) or \
		 	(hunter_vel[0] == -1 and abs(prey_loc[0] - left) <= 6) or \
		 	(hunter_vel[1] == 1 and abs(up - prey_loc[0]) <= 6) or \
		 	(hunter_vel[1] == -1 and abs(prey_loc[0] - down) <= 6):
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

def pipe_width():
	up, down, left, right = get_corners()
	x_width = right - left
	y_width = up - down
	if y_width < x_width:
		return [y_width, "y"]
	else:
		return [x_width, "x"]

def nearest_safe_spot(x, y, width, dimension):
	global prey_loc
	bw_safe = 2 * width
	up, down, left, right = get_corners()
	if dimension == "x":
		min_dist = abs(prey_loc[1] - y)
		min_loc = y
		for loc in range(y, up, bw_safe):
			if abs(prey_loc[1] - loc) < min_dist:
				min_dist = abs(prey_loc[1] - loc)
				min_loc = loc
		for loc in range(down, y, bw_safe):
			if abs(prey_loc[1] - loc) < min_dist:
				min_dist = abs(prey_loc[1] - loc)
				min_loc = loc
		return x, loc
	else:
		min_dist = abs(prey_loc[0] - x)
		min_loc = x
		for loc in range(x, right, bw_safe):
			if abs(prey_loc[0] - loc) < min_dist:
				min_dist = abs(prey_loc[0] - loc)
				min_loc = loc
		for loc in range(left, x, bw_safe):
			if abs(prey_loc[0] - loc) < min_dist:
				min_dist = abs(prey_loc[0] - loc)
				min_loc = loc
		return loc, y


def num_tick_between(x, y, player):
	global hunter_loc
	global prey_loc
	global hunter_vel
	if player == "prey":
		x_diff = abs(x - prey_loc[0])
		y_diff = abs(y - prey_loc[1])
		return 2 * max(x_diff, y_diff)
	else:
		up, down, left, right = get_corners()
		if x - hunter_loc[0] < right - hunter_loc[0]:
			x_diff = x - hunter_loc[0]
		else:
			x_diff = right - hunter_loc[0] + right - x
		if y - hunter_loc[1] < up - hunter_loc[1]:
			y_diff = y - hunter_loc[1]
		else:
			y_diff = up - hunter_loc[1] + up - y
		return max(x_diff, y_diff)
		

	
def can_escape(width, width_dim):
	global hunter_loc
	global hunter_vel
	global prey_loc
	up, down, left, right = get_corners()
	if width <= 10:
		return False, None, None
	#get to safe spot. 
	if width_dim == "x":
		if hunter_vel[0] == 1:
			num_x_ticks = right - hunter_loc[0] - 1
			x_at_wall = right
		else:
			num_x_ticks = hunter_loc[0] - left - 1
			x_at_wall = left
		y_at_wall = num_x_ticks * hunter_vel[1] + hunter_loc[1]
		if y_at_wall < down:
			y_at_wall = (2 * down) - y_at_wall + 1
		elif y_at_wall > up:
			y_at_wall = (2 * up) - y_at_wall - 1
	else:
		if hunter_vel[1] == 1:
			num_y_ticks = up - hunter_loc[1] - 1
			y_at_wall = up
		else:
			num_y_ticks = hunter_loc[1] - down - 1
			y_at_wall = down
		x_at_wall = num_y_ticks * hunter_vel[0] + hunter_loc[0]
		if x_at_wall < left:
			x_at_wall = (2 * left) - x_at_wall + 1
		elif x_at_wall > right:
			x_at_wall = (2 * right) - x_at_wall - 1
	safe_x, safe_y = nearest_safe_spot(x_at_wall, y_at_wall, width, width_dim)
	if num_tick_between(safe_x, safe_y, "hunter") > num_tick_between(safe_x, safe_y, "prey"):
		return True, safe_x, safe_y
	else:
		return False, None, None	


		
def run_away():
	global hunter_loc
	global hunter_vel
	global prey_loc
	if hunter_loc[0] > prey_loc[0]:
		x = -1
	else:
		x = 1
	if hunter_loc[1] > prey_loc[1]:
		y = -1
	else:
		y = 1
	return [x, y]

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

#horizontal wall changes y value
#vertical wall changes x value

def change_velocity(hunter_loc,wall_locations,hunter_vel):
	##print "begin veloc change"
	##print hunter_loc
	if hunter_loc[0] == -1:
		if hunter_loc[1] == -1:
			new_vel = [1,1]
			new_loc = [hunter_loc[0] + new_vel[0],hunter_loc[1] + new_vel[1]]
		elif hunter_loc[1] == 300:
			new_vel = [1,-1]
			new_loc = [hunter_loc[0] + new_vel[0],hunter_loc[1] + new_vel[1]]
		else:
			new_vel = [hunter_vel[0]*-1,hunter_vel[1]]
			new_loc = [hunter_loc[0] + new_vel[0],hunter_loc[1]]
	elif hunter_loc[0] == 300:
		if hunter_loc[1] == -1:
			new_vel = [-1,1]
			new_loc = [hunter_loc[0] + new_vel[0],hunter_loc[1] + new_vel[1]]
		elif hunter_loc[1] == 300:
			new_vel = [-1,-1]
			new_loc = [hunter_loc[0] + new_vel[0],hunter_loc[1] + new_vel[1]]
		else:
			new_vel = [hunter_vel[0]*-1,hunter_vel[1]]
			new_loc = [hunter_loc[0] + new_vel[0],hunter_loc[1]]
	elif hunter_loc[1] == -1: #don't need corner cases because covered in previous if statements
		new_vel = [hunter_vel[0],hunter_vel[1]*-1]
		new_loc = [hunter_loc[0],hunter_loc[1] + new_vel[1]]
	elif hunter_loc[1] == 300: #don't need corner cases because covered in previous if statements
		new_vel = [hunter_vel[0],hunter_vel[1]*-1]
		new_loc = [hunter_loc[0],hunter_loc[1] + new_vel[1]]
	else:
		#not hitting an edge, check if hitting a wall
		hit_wall_vert = False
		hit_wall_horiz = False
		for wall in wall_locations:
			if wall[0] == 0:
				#horizontal
				if wall[1] == hunter_loc[0]:
					if hunter_loc[1] in range(wall[2],wall[3] + 1):
						hit_wall_horiz = True
			elif wall[0] == 1:
				#vertical
				if wall[1] == hunter_loc[1]:
					if hunter_loc[0] in range(wall[2],wall[3] + 1):
						hit_wall_vert = True
		if hit_wall_vert and hit_wall_horiz:
			new_vel = [hunter_vel[0] * -1,hunter_vel[1] * -1]
			new_loc = [hunter_loc[0] + new_vel[0],hunter_loc[1] + new_vel[1]]
		elif hit_wall_horiz:
			new_vel = [hunter_vel[0],hunter_vel[1] * -1]
			new_loc = [hunter_loc[0],hunter_loc[1] + new_vel[1]]
		elif hit_wall_vert:
			new_vel = [hunter_vel[0]*-1,hunter_vel[1]]
			new_loc = [hunter_loc[0] + new_vel[0],hunter_loc[1]]
		else:
			#if no wall is hit, don't change anything
			new_loc = hunter_loc[:]
			new_vel = hunter_vel[:]
	##print "end veloc change"
	##print hunter_loc
	return (new_loc,new_vel)

def ticks_until_meet(hunter_loc,prey_loc,hunter_vel,preymove,wall_locations,wall_delay):
	##print "begin ticks"
	##print hunter_loc,prey_loc
	ticks = 0
	next_steps = hunter_loc[:]
	next_loc_prey = prey_loc[:]
	while True:
		##print hunter_loc,prey_loc
		if next_steps[0] == next_loc_prey[0] - hunter_vel[0] or next_steps[0] == next_loc_prey[0] - 2*hunter_vel[0] :
			##print "breaking cuz wall x"
			##print hunter_loc,prey_loc
			return ticks
		if next_steps[1] == next_loc_prey[1] - hunter_vel[1] or next_steps[1] == next_loc_prey[1] - 2*hunter_vel[1]:
			##print "breaking cuz wall y"
			##print hunter_loc,prey_loc
			return ticks
		if ticks % 2 == 0:
			if preymove:
				next_loc_prey[0] -= hunter_vel[0]
				next_loc_prey[1] -= hunter_vel[1]
		else:
			if not preymove:
				next_loc_prey[0] -= hunter_vel[0]
				next_loc_prey[1] -= hunter_vel[1]
		next_steps[0] += hunter_vel[0]
		next_steps[1] += hunter_vel[1]
		next_steps,hunter_vel = change_velocity(next_steps,wall_locations,hunter_vel) #if hit a wall, make sure new location is correct
		ticks += 1
	##print "end ticks"
	##print hunter_loc,prey_loc
	return ticks #should never happen as only breaks out of the loop when while loop returns

def free_wall(wall_timer,wall_delay,preymove,hunter_vel,hunter_loc,wall_locations,prey_loc):
	global alternate_wall_type
	##print "begin free wall"
	##print hunter_loc,prey_loc
	#the minimum number of ticks until we make a wall to lock them in
	min_ticks_until_wall = ticks_until_meet(hunter_loc,prey_loc,hunter_vel,preymove,wall_locations,wall_delay)
	##print "after ticks"
	##print hunter_loc,prey_loc
	if wall_timer == 0 and min_ticks_until_wall > wall_delay:
		res = alternate_wall_type
		if alternate_wall_type == 1:
			alternate_wall_type = 2
		else:
			alternate_wall_type = 1
	else:
		res = 0
	return res

def make_wall(hunter_loc,hunter_vel,prey_loc,wall_locations,wall_timer,wall_delay,preymove,initial_pass):
	##print "begin make wall"
	##print hunter_loc,prey_loc
	if wall_timer != 0: #if we can't make a wall, don't
		return 0,0
	#check logic when have wifi to see if need to change to -2 depending on what happens when prey moves into wall
	if hunter_loc[0] == prey_loc[0] - hunter_vel[0] or hunter_loc[0] == prey_loc[0] - 2*hunter_vel[0]:
		return 2,2 #x coords are close enough, make horizontal wall
		#make a note about piping a store it to make another horizontal wall
	elif hunter_loc[1] == prey_loc[1] - hunter_vel[1] or hunter_loc[1] == prey_loc[1] - 2*hunter_vel[1]:
		return 1,2 #y coors are close enough, make vertical wall
		#make a note about piping and store it to make another horizontal wall
	elif initial_pass:
		grid_for_hunter = get_corners_idx(hunter_loc,wall_locations)
		grid_for_prey = get_corners_idx(prey_loc,wall_locations)
		#up,down,left,right

		if grid_for_prey == grid_for_hunter:
			##print "begin if grid =="
			##print hunter_loc,prey_loc
			check_free_move = free_wall(wall_timer,wall_delay,preymove,hunter_vel,hunter_loc,wall_locations,prey_loc)
			##print "end check free"
			##print hunter_loc,prey_loc
			if check_free_move != 0:
				#the true here is so we can store a new grid corners
				return check_free_move,1
		return 0,0
	else:
		return 0,0

def get_corners_idx(prey_loc,wall_locations):
	left = -1
	left_idx = None
	right = 300
	right_idx = None
	up = 300
	up_idx = None
	down = -1
	down_idx = None
	for i,wall in enumerate(wall_locations):
		if wall[0] == 0: # horizontal wall
			if wall[1] > prey_loc[1] and wall[1] < up:
				up = wall[1]
				up_idx = i
			if wall[1] < prey_loc[1] and wall[1] > down:
				down = wall[1]
				down_idx = i
		else:  # vertical wall
			if wall[1] < prey_loc[0] and wall[1] > left:
				left = wall[1]
				left_idx = i
			if wall[1] > prey_loc[0] and wall[1] < right:
				right = wall[1]
				right_idx = i
	return [up_idx, down_idx, left_idx, right_idx]


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
initial_pass = True

"""

INPUT DESCRIPTION

0					1		2			3			4						5		6				7				8				9			10
[playerTimeLeft] [gameNum] [tickNum] [maxWalls] [wallPlacementDelay] [boardsizeX] [boardsizeY] [currentWallTimer] [hunterXPos] [hunterYPos] [hunterXVel] 
11				12			13		14			15+
[hunterYVel] [preyXPos] [preyYPos] [numWalls] {wall1 info} {wall2 info} ... 
"""


while True:
	wall_locations = []
	##print "waiting"
	data = sock.recv(4096)
	##print data
	lines = data.split("\n")
	###print data
	###print lines
	if len(lines) == 0:
		##print data
		continue
	line = lines[-2]
	###print line
	###print "recieved:", line
	if line == "done":
		break
	elif line == "hunter":
		hunter_flag = True
		prey_flag = not hunter_flag
		continue
	elif line == "prey":
		piped = False
		run_away_move = None
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
			for i,item in enumerate(recent_data[15:]):
				curr_wall_info.append(item)
				if (i+1)%4 == 0:
					wall_locations.append(curr_wall_info)
					curr_wall_info = []
		#game logic
		preymove = tick_num % 2 != 0 #check if the prey can move during this tick
		if prey_flag:
			move = [0, 0]

			#check if the prey can move during this tick
			preymove = tick_num % 2 != 0 
			if not preymove:
				if prey_flag:
					#if we are the prey, and we can't move, skip this. Could do computation here later
					result = [game_num, tick_num, 0, 0]
			# we can move...do something
			else:
				in_pipe, direction, wall = detect_pipe()
				width, width_dim = pipe_width()
				if not in_pipe:
					if piped and width >= 50:
						piped = False
					if not piped:
						# if near corner, go the other way
						corner, move[0], move[1] = near_corner()
						if corner == False:
							if near_wall() == False:
								# just follow the hunter at a safe distance
								move = follow_hunter()
					else:
						if run_away_move != None:
							move = run_away_move
						# in a pipe with hunter
						else:
							escape, move[0], move[1] = can_escape(width,width_dim)
							# if not, RUN AWAY
							if not escape:
								run_away_move = run_away()
								move = run_away_move

				else:
					if not piped:
						piped = True
					x, y, ticks = hunter_hit_pipe(direction, wall)
					aim_x, aim_y = stop_near_hunter(x, y, ticks, direction, wall)
					if aim_x > prey_loc[0]:
						move[0] = 1
					elif aim_x < prey_loc[0]:
						move[0] = -1
					if aim_y > prey_loc[1]:
						move[1] = 1
					elif aim_y < prey_loc[1]:
						move[1] = -1
					# We are in a pipe
					#move[0] = 1 #movement in x direction
					#move[1] = 1 #movement in y direction
				result = [game_num,tick_num,move[0], move[1]]
		if hunter_flag:
			if initial_pass == True and hunter_vel != [1,1]:
				initial_pass = False
			wall_to_add = 0 #type of wall to add. Initialized at no wall. 1 is horizontal and 2 is vertical
			walls_to_delete = [] #list of wall indicies to delete (indicies are from the list of walls created, not the location of the wall on the grid)
			#-----------------------------------------------------------------------#
			#  hunter logic (determine whether to make a wall and/or delete walls)  #
			##print "Into the rabbit hole we go"
			##print hunter_loc,prey_loc
			wall_to_add,free = make_wall(hunter_loc,hunter_vel,prey_loc,wall_locations,time_until_place_wall,wall_delay,preymove,initial_pass)
			#print wall_to_add,free
			##print "Out of the rabbit hole we came"
			##print hunter_loc,prey_loc
			##print hunter_loc
			if free == 2:
				initial_pass = False
				#print hunter_loc,prey_loc
				#break
			grid_for_hunter = get_corners_idx(hunter_loc,wall_locations)

				#wall_locations.append([1,hunter_loc[0],left,right])

			##print hunter_loc, next_location
			#grid_for_hunter = get_corners_idx(next_location,wall_locations)
			grid_for_prey = get_corners_idx(prey_loc,wall_locations)
			#print free,wall_to_add
			if wall_to_add != 0 and num_walls == 2 and initial_pass:
				if free == 2:
					initial_pass = False
				for i,wall in enumerate(wall_locations):
					if wall[0] + 1 == wall_to_add:
						walls_to_delete.append(i)

			if not initial_pass and wall_to_add != 0:
				if wall_to_add == 1:
					if hunter_vel[1] == 1:
						#print "DELETING BOTTOM"
						#coming from the bottom
						if grid_for_hunter[1]:
							walls_to_delete.append(grid_for_hunter[1])
					else:
						#coming from top
						if grid_for_hunter[0]:
							walls_to_delete.append(grid_for_hunter[0])
				else:
					if hunter_vel[0] == 1:
						#coming from left
						if grid_for_hunter[2]:
							walls_to_delete.append(grid_for_hunter[2])
					else:
						#coming from the right
						if grid_for_hunter[3]:
							walls_to_delete.append(grid_for_hunter[3])

			#check if we are in same subgrid as the prey
			#if we are, delete irrelevant walls
			#this should include the wall we are making
			#if this is not the case, by our logic, the prey should be trapped and we should have alternate logic
			#-----------------------------------------------------------------------#
			#print wall_locations
			if len(walls_to_delete) == 0:
				result = [game_num,tick_num,wall_to_add]
			else:
				#print "deleting walls"
				result = [game_num,tick_num,wall_to_add] + walls_to_delete
		result_to_send = ' '.join(map(str,result)) #convert results to strings so socket can read
	print "sending:", result_to_send
	sock.sendall(result_to_send + "\n") #send to socket
sock.close()