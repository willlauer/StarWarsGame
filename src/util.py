import pygame
import math

# Store the pathnames for everything, starting from the src directory
ball_pathname = '../res/ball.png'
laser_pathname = '../res/energy_ball.png'
explosion_pathname = '../res/pg_explosion.png'

background_pathname = '../res/background-stars.png'

star_wars_theme = '../res/star-wars-theme-song.wav'
imperial_march = '../res/imperial_march.wav'
duel_of_the_fates = '../res/Star-Wars-Duel-of-the-Fates.wav'

rand1 = '../res/chewy_roar.wav'
rand2 = '../res/forcestrong.wav'
rand3 = '../res/900yearsold.wav'
rand4 = '../res/laughfuzzball.wav'

crash_sound = '../res/doh1.wav'

cap_speed = False 
max_death_star_speed = 5

blaster_sound = '../res/blaster-firing.wav'
explosion_sound = '../res/Explosion10.wav'
archer_theme = '../res/archer-theme-song.wav'

xwing_base_path = '../res/from_'
xwing_positions = ['top', 'bottom', 'left', 'top_left', 'top_right']

health_x, health_y = 0, 0

# How much time (in seconds) passes for each iteration
time_step = 1 

screen_width, screen_height = 640, 640 
ball_width, ball_height = 70, 70 

laser_width, laser_height = 10, 10
xwing_width, xwing_height = 40, 40

explosion_width, explosion_height = int(xwing_width * 1.2), int(xwing_height * 1.2) # Slightly larger than the xwing

laser_velocity = 6

xwing_velocity = 2

max_steering = 50 # Determines how fast the xwings can turn

spawning_interval = 100

explosion_duration = 100

damage_per_hit = 10
points_per_xwing_destroyed = 10

score_coords = 10, 10 # Col, row

spawn_rate = 0.95 # Make this higher to make the game easier. A lower spawn_rate means more frequent spawns


# The list of all keys for which we may take some action
action_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_ESCAPE, pygame.K_RSHIFT]
movement_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT]

init_ball_x = screen_height // 2
init_ball_y = screen_width // 2

# Move down and to the right to get the ball center coordinate from the top left 
# coordinates
def ball_center(x, y):
	return x + ball_height // 2, y + ball_height // 2

# Move up and to the left to get the ball's corner coordinates given the center
# coordinates
def ball_corner(x, y):
	return x - ball_height // 2, y - ball_height // 2


# Returns a set of pygame.key objects
def get_movement_keys(pressed, state):
	return {x for x in movement_keys if x in pressed}


def initial_blit_locations():
	il = {}
	il['ball'] = (init_ball_x, init_ball_y)
	return il

def load_scaled_blits():
	'''
	Return a dict from the constantly-sized object to their blits
	'''	
	sb = {}

	ball = pygame.image.load(ball_pathname)
	ball = pygame.transform.scale(ball, (ball_width, ball_height))
	sb['ball'] = ball

	laser = pygame.image.load(laser_pathname)
	laser = pygame.transform.scale(laser, (laser_width, laser_height))
	sb['laser'] = laser

	explosion = pygame.image.load(explosion_pathname)
	explosion = pygame.transform.scale(explosion, (explosion_width, explosion_height))
	sb['explosion'] = explosion

	background = pygame.image.load(background_pathname)
	background = pygame.transform.scale(background, (int(screen_width * 2.0), int(screen_height * 2.0)))
	sb['background'] = background

	for position in xwing_positions:
		sb['xwing_' + str(position)] = pygame.image.load(xwing_base_path + position + '.png')
		sb['xwing_' + str(position)] = pygame.transform.scale(sb['xwing_' + str(position)], (xwing_width, xwing_height))

	return sb

def all_pixels():
	return {(i, j) for i in range(screen_height) for j in range(screen_width)}

def normed_distance(a, b): 
	'''
	Return the normalized vector between two points
	Kinda depends on the order - a is the target and b is the current
	'''
	lx = a[0] - b[0]
	ly = a[1] - b[1]
	l = math.sqrt(lx ** 2 + ly ** 2)
	lx2, ly2 = lx / l, ly / l
	return lx2, ly2

def norm_components(v):
	'''
	Return the unit vector corresponding to the given location
	'''
	sx = 1 if v[0] >= 0 else -1
	sy = 1 if v[1] >= 0 else -1
	l = math.sqrt(v[0] ** 2 + v[1] ** 2)
	return sx * v[0] / l, sy * v[1] / l

def scaled_distance(a, b, c):
	'''
	Return the scaled distance between two points
	'''
	x, y = normed_distance(a, b)
	return x * c, y * c

def truncate(v, l):
	'''
	Truncate a given vector
	'''
	orig_length = math.sqrt(v[0] ** 2 + v[1] ** 2)
	if orig_length <= l:
		return v
	else:	
		uvec_x, uvec_y = norm_components(v)
		return uvec_x * l, uvec_y * l


