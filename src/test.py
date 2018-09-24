import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Hello World')
pygame.mouse.set_visible(1)

done = False
clock = pygame.time.Clock()

while not done:
	clock.tick(60)

	keyState = pygame.key.get_pressed()

	if keyState[pygame.K_ESCAPE]:
		print('\nGame Shuting Down!')
		done = True
	pygame.event.pump()

