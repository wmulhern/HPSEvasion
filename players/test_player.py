#imports

import socket
import random
import sys
import time
import random

trap_flag = False
alternate_wall_type = 1

#functions


def delete_walls(max_walls,num_walls,hunter_loc,prey_loc,wall_locations):
	#logic
	#	1 - if wall is doing nothing and only a couple walls left to make, delete walls doing nothing
	#	2 - if max walls == num walls, delete the least impactful wall
	#	3 - if hunter and prey are in different quadrants, delete wall to open them up 
	#	4 - ?
	#look up wall logic regarding how to tell full wall location
	pass

#horizontal wall changes y value
#vertical wall changes x value

def change_velocity(hunter_loc,wall_locations,hunter_vel):
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
			new_loc = hunter_loc
			new_vel = hunter_vel
	return (new_loc,new_vel)

def ticks_until_meet(hunter_loc,prey_loc,hunter_vel,preymove,wall_locations,wall_delay):
	ticks = 0
	next_steps = hunter_loc
	next_loc_prey = prey_loc
	while True:
		if ticks > wall_delay:
			return ticks
		if next_steps[0] == next_loc_prey[0] - 1*hunter_vel[0]:
			return ticks
		if next_steps[1] == next_loc_prey[1] - 1*hunter_vel[1]:
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
		next_steps,hunter_vel = change_velocity(hunter_loc,wall_locations,hunter_vel) #if hit a wall, make sure new location is correct
		ticks += 1
	return ticks #should never happen as only breaks out of the loop when while loop returns

def free_wall(wall_timer,wall_delay,preymove,hunter_vel,hunter_loc,wall_locations,prey_loc):
	global alternate_wall_type
	#the minimum number of ticks until we make a wall to lock them in
	min_ticks_until_wall = ticks_until_meet(hunter_loc,prey_loc,hunter_vel,preymove,wall_locations,wall_delay)
	if wall_timer == 0 and min_ticks_until_wall > wall_delay:
		res = alternate_wall_type
		if alternate_wall_type == 1:
			alternate_wall_type = 2
		else:
			alternate_wall_type = 1
	else:
		res = 0
	return res

def make_wall(hunter_loc,hunter_vel,prey_loc,wall_locations,wall_timer,wall_delay,preymove):
	if wall_timer != 0: #if we can't make a wall, don't
		print "cant do shit"
		return 0
	#check logic when have wifi to see if need to change to -2 depending on what happens when prey moves into wall
	if hunter_loc[0] == prey_loc[0] - 1*hunter_vel[0]:
		return 1 #x coords are close enough, make horizontal wall
		#make a note about piping a store it to make another horizontal wall
	elif hunter_loc[1] == prey_loc[1] - 1*hunter_vel[0]:
		return 2 #y coors are close enough, make vertical wall
		#make a note about piping and store it to make another horizontal wall
	else:
		grid_for_hunter = get_corners(hunter_loc,wall_locations)
		grid_for_prey = get_corners(prey_loc,wall_locations)
		#up,down,left,right

		if grid_for_prey == grid_for_hunter:
			check_free_move = free_wall(wall_timer,wall_delay,preymove,hunter_vel,hunter_loc,wall_locations,prey_loc)
			if check_free_move != 0:
				#the true here is so we can store a new grid corners
				return check_free_move
		return 0

def get_corners(prey_loc,wall_locations):
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
		prey_flag = True
		hunter_flag = not prey_flag
		continue
	elif line == "sendname":
		result_to_send = "NoEscape"
	else:
		#we received game state
		recent_data = map(int,line.split()) #get the last line from the socket
		print recent_data
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
		preymove = tick_num % 2 != 0 #check if the prey can move during this tick
		if prey_flag:
			if not preymove:
				if prey_flag:
					#if we are the prey, and we can't move, skip this. Could do computation here later
					result = [game_num, tick_num, 0, 0]
			else:
				x = 0 #movement in x direction
				y = 0 #movement in y direction
				#----------------------------------#
				#  prey logic (determine x and y)  #
				# random logic for now
				x += random.choice([0,1,-1])
				y += random.choice([0,1,-1])
				#----------------------------------#
				result = [game_num,tick_num,x,y]
		if hunter_flag:
			wall_to_add = 0 #type of wall to add. Initialized at no wall. 1 is horizontal and 2 is vertical
			walls_to_delete = [] #list of wall indicies to delete (indicies are from the list of walls created, not the location of the wall on the grid)
			#-----------------------------------------------------------------------#
			#  hunter logic (determine whether to make a wall and/or delete walls)  #
			grid_for_hunter = get_corners(hunter_loc,wall_locations)
			grid_for_prey = get_corners(prey_loc,wall_locations)
			#up,down,left,right

			if grid_for_prey == grid_for_hunter:
				corners = [
					[grid_for_hunter[2],grid_for_hunter[0]],
					[grid_for_hunter[3],grid_for_hunter[0]],
					[grid_for_hunter[2],grid_for_hunter[1]],
					[grid_for_hunter[3],grid_for_hunter[1]]
				]
				for i,wall in enumerate(wall_locations):
					for corner in grid_for_hunter:
						if wall[0] == 0:
							locations = [[item,wall[1]] for item in range(wall[2],wall[3] + 1)]
						else:
							locations = [[wall[1],item] for item in range(wall[2],wall[3] + 1)]
						if corner not in locations:
							walls_to_delete.append(i)

			wall_to_add = make_wall(hunter_loc,hunter_vel,prey_loc,wall_locations,time_until_place_wall,wall_delay,preymove)
			print wall_to_add
			#check if we are in same subgrid as the prey
			#if we are, delete irrelevant walls
			#this should include the wall we are making
			#if this is not the case, by our logic, the prey should be trapped and we should have alternate logic
			#-----------------------------------------------------------------------#
			if len(walls_to_delete) == 0:
				result = [game_num,tick_num,wall_to_add]
			else:
				result = [game_num,tick_num,wall_to_add] + walls_to_delete
		result_to_send = ' '.join(map(str,result)) #convert results to strings so socket can read
	print "sending:", result_to_send
	sock.sendall(result_to_send + "\n") #send to socket
sock.close()

