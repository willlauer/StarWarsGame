import pygame
from pygame.locals import *
import util
import colors

class Credits:
	
	def __init__(self):
		
		pygame.init()
		pygame.font.init()
		self.myfont = pygame.font.SysFont('helvetica', 12)

		self.screen = pygame.display.set_mode((util.screen_width, util.screen_height))
	
	def exit_credits(self, score):
		clock = pygame.time.Clock()
		credits_text = 'Congratulations!\n\nYou hit %d Rebel ships,\n\nearning a score of %d!\n\n\n\nCreated by Will Lauer,\n\nwith special thanks to Thomas Lauer\n\n\nfor bailing his brother out when it came to working with Gimp.\n\n\nThank you for playing!' % (score, score // 10) 

		credits = self.myfont.render(credits_text, False, colors.blue)

		clock.tick(60)
		self.screen.fill(colors.blue)
		#for i in range(util.screen_height - 1, 0, -1):
		#	self.screen.blit(credits, (10, i))
		#	pygame.display.flip()
		self.screen.blit(credits, (10, 10))	
		pygame.display.flip()
		

#		pygame.display.quit()
#		pygame.quit()
