import pygame
import util
import math 

gravity = 10 # Acceleration due to gravity
	
ball_weight = 100 # kg
force = 10 # Newtons
time_step = 1

# Change in position with the given velocity and acceleration
def displacement(velocity, acceleration, time_step):
	return velocity * time_step + (acceleration * (time_step ** 2)) / 2

# Return the new velocity after a time step with the given acceleration applied
def velocity1(velocity0, acceleration, time_step):
	return velocity0 + acceleration * time_step

# Force to acceleration
def acceleration(f, m):
	return f / m
	
	
def do_movement(movement_keys, state):
	
	# Idea is that movement keys apply force in different directions
	# We only have nonzero acceleration when a key is pressed
	
	hit_perimeter = False

	# Reset the acceleration in the state at each point
	ax, ay = 0.0, 0.0
	
	# Determine acceleration in the vertical (+/- x) direction
	if pygame.K_UP in movement_keys:
		ax -= acceleration(force, ball_weight)
	if pygame.K_DOWN in movement_keys:
		ax += acceleration(force, ball_weight)

	# Determine acceleration in the horizontal (+/- y) direction
	if pygame.K_LEFT in movement_keys:
		ay -= acceleration(force, ball_weight)
	if pygame.K_RIGHT in movement_keys:
		ay += acceleration(force, ball_weight)
	
	# Compute the new x and y velocity after a timestep
	vx1 = velocity1(state['vx'], ax, time_step)
	vy1 = velocity1(state['vy'], ay, time_step)

	if util.cap_speed:
		vx1 = util.max_death_star_speed if util.max_death_star_speed < vx1 else vx1
		vy1 = util.max_death_star_speed if util.max_death_star_speed < vy1 else vy1 


	dx = displacement(state['vx'], ax, time_step)
	dy = displacement(state['vy'], ay, time_step)

	# Ensure we don't keep modifying the position and velocity if it would cause
	# the player to run off the screen
	if state['x'] < 0 and vx1 < 0 or state['x'] > util.screen_height and vx1 > 0:
		vx1 = 0.0
		dx = 0.0
	if state['y'] < 0 and vy1 < 0 or state['y'] > util.screen_width and vy1 > 0:
		vy1 = 0.0
		dy = 0.0

	# Update the state information about our vx and vy values
	state['vx'] = vx1
	state['vy'] = vy1

	# Update the location of the ball
	state['x'] = state['x'] + dx
	state['y'] = state['y'] + dy
		
# Components of the laser's trajectory
def get_laser_trajectory(target, state):

	lx2, ly2 = util.normed_distance(target, (state['x'], state['y']))

	# Laser velocity * x and y components of the unit vector
	lx2, ly2 = util.laser_velocity * lx2, util.laser_velocity * ly2
	return lx2, ly2
