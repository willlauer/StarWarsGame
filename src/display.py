import pygame 
from pygame.locals import * 
import util
import colors

class Display:

	def __init__(self):

		pygame.font.init()
		self.myfont = pygame.font.SysFont('helvetica', 30)
		
		self.background_blits = []
		self.foreground_blits = ['ball']

		self.scaled_blits = util.load_scaled_blits()
		self.blit_locations = util.initial_blit_locations()
		self.screen = pygame.display.set_mode((util.screen_width, util.screen_height))

		self.explosion_counters = {} # Store the number of frames we've seen each explosion
	
		# Since many xwing ids may map to the same sprite, add the mapping here
		# As a bonus, if we want to change the orientation, we can do so by modifying this map
		self.xwing_sprite_map = {}

	def exit_credits(self, state):
		clock = pygame.time.Clock()		
		credits_text = 'Congratulations!\n\nYou hit %d Rebel ships,\n\nearning a score of %d!\n\n\n\nCreated by Will Lauer,\n\nwith special thanks to Thomas Lauer\n\n\nfor bailing his brother out when it came to working with Gimp.\n\n\nThank you for playing!' % (state['score'], state['score'] // 10)
		credits = self.myfont.render(credits_text, False, colors.white)
		for i in range(util.screen_height - 1, 0 - util.screen_height, -1):
			self.screen.blit(credits, (10, i))
			pygame.display.update()
			clock.tick(60)
		
				
	def update_ball_position(self, state):
		'''
		Pygame wants the column coordinate to come before the row coordinate
		'''
		self.blit_locations['ball'] = util.ball_corner(state['y'], state['x'])	

	def update_lasers(self, state):
		'''
		Iterate through all lasers in the game state, deleting ones that are now out of bounds,
		and updating the positions of all the others
		'''
		lasers = state['lasers']
		new_lasers = lasers.copy()
		for k in lasers:
			if lasers[k][0] < 0 or lasers[k][0] > util.screen_height \
			or lasers[k][1] < 0 or lasers[k][1] > util.screen_width:
				# The laser is out of bounds and should be deleted
				new_lasers.pop(k, None) # both from the lasers
				self.background_blits.remove(k)
			else:
				# The laser is still in bounds and should be included
				x, y, vx, vy = lasers[k]
				new_x, new_y = x + vx * util.time_step, y + vy * util.time_step
				new_lasers[k] = new_x, new_y, vx, vy
				self.blit_locations[k] = new_y, new_x

		state['lasers'] = new_lasers
		
	'''
	For each xwing, check its velocity and orientation and if necessary,
	change the orientation sprite so that the two conform
	'''
	def update_orientation(self, xwing, orientation):
		self.xwing_sprite_map[xwing] = self.scaled_blits['xwing_' + str(orientation)]

	def update_xwings(self, state):
		
		# Update the position of each of the xwings
		xwings = state['xwings']
		new_xwings = xwings.copy()
		for xw in xwings:
			if xwings[xw][1] < 0 or xwings[xw][1] > util.screen_height \
			or xwings[xw][2] < 0 or xwings[xw][2] > util.screen_width:
				# The xwing is out of bounds and should be deleted
				new_xwings.pop(xw, None)
				self.foreground_blits.remove(xw)
			else:
				# The xwing is still in bounds and should be included
				o, x, y, vx, vy = xwings[xw]
				new_x, new_y = x + vx * util.time_step, y + vy * util.time_step
				self.blit_locations[xw] = new_y, new_x

		state['xwings'] = new_xwings

	# We had a collision, so run the explosion animation and remove the xwing from the blits	
	def boom(self, xwing_id):
		self.foreground_blits.remove(xwing_id)
		self.foreground_blits.append('e' + str(xwing_id[1:])) # Explosions enumerated e0, e1, e...
		self.explosion_counters['e' + str(xwing_id[1:])] = 0


	def remove_laser(self, laser_id):
		self.background_blits.remove(laser_id)

	# Just add the corresponding id to the blit dicts
	def add_xwing(self, i, orientation):
		self.foreground_blits.append(i)
		self.xwing_sprite_map[i] = self.scaled_blits['xwing_' + str(orientation)]
			
	def add_laser(self, i):
		self.background_blits.append(i)

	def update_health(self, state):
		health_per_hit = util.screen_width // 100
		health_bar_width = health_per_hit * state['health']
		pygame.draw.rect(self.screen, colors.blue, [util.health_x, util.health_y, health_bar_width, 50], 0)

	def update_score(self, state):
		text = self.myfont.render('Score: ' + str(state['score']), False, colors.white)
		self.screen.blit(text, util.score_coords)

	def update(self, state):
		'''
		Take in the state object stored by Game, and update blits
		Start off by just updating the ball location
		'''

		self.update_ball_position(state)
		self.update_lasers(state)
		self.update_xwings(state)

		self.screen.fill((colors.black)) # Fill the background
		# self.screen.blit(self.scaled_blits['background'], (-100, -50))
		self.update_health(state) # Gotta come after screen.fill, otherwise its covered up
		self.update_score(state)

		# Blit everything with updated locations
		for name in self.background_blits:
			if name[0] == 'l':
				self.screen.blit(self.scaled_blits['laser'], self.blit_locations[name])
			else:
				self.screen.blit(self.scaled_blits[name], self.blit_locations[name])
		for name in self.foreground_blits:
			if 'e' in name:
				if 'x' + str(name[1:]) not in self.blit_locations:
					continue
				self.screen.blit(self.scaled_blits['explosion'], self.blit_locations['x' + str(name[1:])])
				self.explosion_counters[name] += 1
			elif 'x' in name:
				# We are adding an xwing, so need to find the proper sprite
				sprite = self.xwing_sprite_map[name]
				blit_loc = self.blit_locations[name]
				self.screen.blit(self.xwing_sprite_map[name], self.blit_locations[name])
			else:
				self.screen.blit(self.scaled_blits[name], self.blit_locations[name])

		# Make it visible
		pygame.display.flip()

		# Remove explosions after their duration is up
		new_explosion_counters = {}
		for e in self.explosion_counters:
			if self.explosion_counters[e] == util.explosion_duration:
				self.foreground_blits.remove(e)
			else:
				new_explosion_counters[e] = self.explosion_counters[e]
		self.explosion_counters = new_explosion_counters

			
