import pygame
import util
import physics
from display import Display
import random
import colors
import time

class Game:
	
	def __init__(self):
		
		pygame.init()	
	
		self.spawning_interval = util.spawning_interval

		# If this is true, we have just a blank screen and the ball. For playing
		# around with the physics
		self.basic = True
	
		self.display = Display()

		self.laserID = 0
		self.xwingID = 0
		
		# Track info about the player in the world
		self.state = \
		{
			'vx': 0.0, # Velocity in the x and y directions
			'vy': 0.0,
			'x': util.init_ball_x,
			'y': util.init_ball_y,
			'health': 100, 
			'counter': 0,
			'score': 0,
			'done': False, # Set to true when the player loses
			'lasers': {}, # Store as a dict of {id: (x, y, vx, vy)}
			'xwings': {} # Store info about xwings
				# id: orientation, x, y, velocity
		}

		self.can_fire = True	
		self.can_play_sound = True

		self.main_theme = pygame.mixer.Sound(util.star_wars_theme)
		self.imperial_march = pygame.mixer.Sound(util.imperial_march)	
		self.duel_of_the_fates = pygame.mixer.Sound(util.duel_of_the_fates)
		
		self.blaster_sound = pygame.mixer.Sound(util.blaster_sound)
		self.blaster_channel = pygame.mixer.Channel(1)
		self.explosion_channel = pygame.mixer.Channel(2)
		self.explosion_sound = pygame.mixer.Sound(util.explosion_sound)

		self.crash_sound = pygame.mixer.Sound(util.crash_sound)

		self.random_sounds = [pygame.mixer.Sound(util.rand2)] # only really enjoyed the darth vader clip so far



		
	def move_ball(self, movement_keys):
		'''
		Update the ball position
		'''
		physics.do_movement(movement_keys, self.state)	
		self.display.update(self.state)
	



	def add_laser_bolt(self, tx, ty):
		'''
		Add a new laser bolt with starting position self.state['x'], self.state['y'] and 
		trajectory tx, ty
		'''
		self.state['lasers']['l' + str(self.laserID)] = (self.state['x'], self.state['y'], tx, ty)
		self.display.add_laser('l' + str(self.laserID))
		self.laserID += 1



	def fire_laser(self, target): # target passed in as col, row
		'''
		Get the trajectory of the new laser bolt, add it to the game state, and update the display
		'''
		true_target = target[1], target[0]
		tx, ty = physics.get_laser_trajectory(true_target, self.state)
		self.add_laser_bolt(tx, ty)
		self.display.update(self.state)
		pygame.mixer.Channel(1).play(self.blaster_sound)



	def reached_end(self): 
		'''
		Check whether the ball is within the target area
		'''
		if self.basic:
			return False
		return (self.state['x'] >= self.goal_x and self.state['x'] <= self.goal_x + self.goal_height) \
		and (self.state['y'] >= self.goal_y and self.state['y'] <= self.goal_y + self.goal_width)



	def xwing_initial_position(self, orientation):	
		'''
		Depending on the orientation, there will be a different range of possible initial locations
		for the xwing
		'''
		# Return row, col coordinate
		if orientation == 'top':
			return 0, random.randint(0, util.screen_width - 1)
		if orientation == 'bottom':
			return util.screen_height - 1, random.randint(0, util.screen_width - 1)
		if orientation == 'left':
			return random.randint(0, util.screen_height - 1), 0
		if orientation == 'right':
			return random.randint(0, util.screen_height - 1), util.screen_width - 1

		# If orientation is top_left or top_right, we have a choice in which to use
		# So just recurse once with a hard orientation specified
		if orientation == 'top_left':
			po = random.randint(0, 1)
			particular_orientation = 'top' if po == 1 else 'left'
			return self.xwing_initial_position(particular_orientation)
		if orientation == 'top_right':
			po = random.randint(0, 1)
			particular_orientation = 'top' if po == 1 else 'right'
			return self.xwing_initial_position(particular_orientation)
	
	
	def omniscient_seeking(self, i):
		'''
		Assume the xwings can see everything and they always angle toward the player
		Returns a new velocity that angles them toward the player
		'''
		orientation, x, y, vx, vy = self.state['xwings'][i]
		x = x + util.xwing_height // 2 # Update so we try to match the centers
		y = y + util.xwing_width // 2
		target_x, target_y = self.state['x'], self.state['y']	
		desired_velocity = util.scaled_distance((target_x, target_y), (x, y), util.xwing_velocity)
		steering = util.truncate((desired_velocity[0] - vx, desired_velocity[1] - vy), util.max_steering)
		
		# Update the x and y velocity with the steering components
		fin_vx, fin_vy = vx + steering[0], vy + steering[1]	 
		return fin_vx, fin_vy

	def spawn_xwing(self):
		'''
		Spawn an xwing
		'''
		#if self.xwingID > 3:
		#	return 
		xwing_id = 'x' + str(self.xwingID) # pull the next xwing id
		orientation = util.xwing_positions[random.randint(0, len(util.xwing_positions) - 1)] # (-1 to keep it in bounds)
		init_x, init_y = self.xwing_initial_position(orientation)
		
		# Start with velocity = 0, to be updated directly in the direction of the player
		# on the next iteration of omniscient_seeking
		# Set the state for our new xwing 
		self.state['xwings'][xwing_id] = orientation, init_x, init_y, 0, 0 
		
		# Add the id of this xwing to the things to be blitted 
		self.display.add_xwing(xwing_id, orientation)

		self.xwingID += 1


	def do_actions(self):	
		'''
		Handle all user-side actions
		'''
		key_state = pygame.key.get_pressed()
		pressed_keys = {x for x in util.action_keys if key_state[x]}
		
		# Handle avatar movement
		movement_keys = util.get_movement_keys(pressed_keys, self.state)	
		self.move_ball(movement_keys)

		if pygame.mouse.get_pressed()[0] and self.can_fire:
			# Then we have pressed some part of the mouse
			target = pygame.mouse.get_pos()
			self.fire_laser(target)
			self.can_fire = False
		if not pygame.mouse.get_pressed()[0]:
			self.can_fire = True

		# Reset to catch the next actions
		pygame.event.pump()	



	def update_xwing_position(self, xwing_id):
		'''
		Self-explanatory - update the position of the given xwing according to
		its current velocity
		'''
		# Modify the xy coordinates of the xwing according to the current velocity
		o, x, y, vx, vy = self.state['xwings'][xwing_id]
		self.state['xwings'][xwing_id] = o, x + vx, y + vy, vx, vy



	def update_xwing_velocity(self, xwing_id):
		'''
		Modify the state to contain the updated xwing velocity according to our seeking
		behavior
		'''
		updated_v = self.omniscient_seeking(xwing_id)
		o, x, y, vx, vy = self.state['xwings'][xwing_id]
	
		# Also update orientation
		if updated_v[0] < 0 and updated_v[1] > 0:
			new_o = 'left'
		elif updated_v[0] < 0 and updated_v[1] < 0:
			new_o = 'bottom'
		elif updated_v[0] > 0 and updated_v[1] < 0:
			new_o = 'top_right'
		else: # updated_v[0] > 0 and updated_v[1] > 0
			new_o = 'top_left'

		if new_o != o:
			self.display.update_orientation(xwing_id, new_o)
			
	
		self.state['xwings'][xwing_id] = new_o, x, y, updated_v[0], updated_v[1]



	def handle_spawning(self):
		'''	
		Depending on the game state, add some number of new xwings 
		'''
		if self.state['counter'] % self.spawning_interval == 0:
			self.spawn_xwing()
			self.spawning_interval = max(15, int(self.spawning_interval * util.spawn_rate))




	def handle_ai(self):
		'''
		Do spawning, and update position and velocity for all the xwing 
		'''
		self.handle_spawning()

		# Update the movement pattern and position of each xwing 
		for xwing_id in self.state['xwings']:
			self.update_xwing_velocity(xwing_id)
			self.update_xwing_position(xwing_id)


	def handle_collision(self, xwing_id):
		'''
		This xwing has collided with the death star, so update its status
		'''
		self.state['xwings'].pop(xwing_id)
		self.display.boom(xwing_id)


	def check_for_destroyed_xwings(self):
		'''
		Compare the location of each laser with the xwings 
		'''
		destroyed = []
		finished_lasers = []
		for xwing in self.state['xwings']:
			_, x, y, _, _ = self.state['xwings'][xwing]
			for laser in self.state['lasers']:
				lx, ly, _, _ = self.state['lasers'][laser]
				lx, ly = int(lx), int(ly)
				if lx in range(int(x), int(x + util.xwing_height))\
				and ly in range(int(y), int(y + util.xwing_width)):
					# We have a collision
					self.explosion_channel.play(self.explosion_sound)
					destroyed.append(xwing)
					finished_lasers.append(laser)
					self.display.boom(xwing)
					break

		# Remove destroyed xwings 
		for d in destroyed:
			self.state['xwings'].pop(d)

		return len(destroyed)
			

	def check_collisions(self):
		'''
		If any of the xwings have collided with the player,
		update the health of the death star
		'''
		ds_coords = self.state['x'], self.state['y']
	
		xwings_to_remove = []
		num_collisions = 0
		for xwing_id in self.state['xwings']:
			_, x, y, _, _ = self.state['xwings'][xwing_id]
			xcx = int(x + util.xwing_height // 2)
			xcy = int(y + util.xwing_width // 2)
			
			# This only checks if the center of the xwing sprite is within the bounds of the death star sprite
			if xcx in range(int(ds_coords[0] - util.ball_height // 2), int(ds_coords[0] + util.ball_height // 2))\
			and xcy in range(int(ds_coords[1] - util.ball_width // 2), int(ds_coords[1] + util.ball_width // 2)):
				xwings_to_remove.append(xwing_id)
				num_collisions += 1

		for xwing in xwings_to_remove:
			self.handle_collision(xwing)

		return num_collisions	



	def update_health(self, num_collisions):
		'''
		Update our health statistic according to the number of collisions this past frame
		'''
		diff = num_collisions * util.damage_per_hit
		self.state['health'] -= diff
		
		# If health drops below 0, we've lost
		if self.state['health'] <= 0:
			self.state['health'] = 0
			self.state['done'] = True

	def update_score(self, num_destroyed):
		'''
		We get points for xwings destroyed with lasers
		'''
		points = num_destroyed * util.points_per_xwing_destroyed
		self.state['score'] += points
		if self.state['score'] % 300 == 0 and self.state['score'] > 0 and self.can_play_sound:
			rsound = self.random_sounds[random.randint(0, len(self.random_sounds) - 1)]
			pygame.mixer.Channel(3).play(rsound)

			# Like a mutex, until we are guaranteed we can play on this channel again
			self.can_play_sound = False



	def play_level(self, level):
		'''
		Call this for each level
		If level is the string 'basic', then don't load any tiles and just use
		the default display
		'''
		clock = pygame.time.Clock()
	
		while not self.state['done']:
			clock.tick(60) 
			self.state['counter'] += 1
			self.do_actions()
			self.handle_ai()
			num_collisions = self.check_collisions()
			if num_collisions > 0:
				self.explosion_channel.play(self.explosion_sound)		
			points = self.check_for_destroyed_xwings()

			# This is so that we don't get stuck in a temporary loop were the score
			# is at a checkpoint, and hasn't changed, causing the player to try playing
			# the sound bit over and over again
			if points > 0:
				self.can_play_sound = True
			self.update_health(num_collisions)
			self.update_score(points)

			# Update the display once per iteration, after all changes have been made
			self.display.update(self.state)
		
		print('Well done!')
		print('You hit %s rebel fighters,' % str(self.state['score'] // 10))
		print('for a score of %s' % str(self.state['score']))
		# self.display.exit_credits(self.state)

	def run(self):
		'''
		Point of entry to the Game class
		'''
		done = False
	
		# Set the song order
		pygame.mixer.Channel(0).play(self.main_theme)
		pygame.mixer.Channel(0).queue(self.imperial_march)
		pygame.mixer.Channel(0).queue(self.main_theme)
		pygame.mixer.Channel(0).queue(self.imperial_march)
		pygame.mixer.Channel(0).queue(self.duel_of_the_fates)
		
		level = 0 # Irrelevant if self.basic is True
		self.play_level(level)

		pygame.event.wait()

		pygame.display.quit()
		pygame.quit()


