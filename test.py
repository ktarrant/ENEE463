import sys
import math
import bird
#import and init pygame
import pygame

pygame.init()



#create the screen
window = pygame.display.set_mode((640, 480))

# colors
black = (0, 0, 0)

# what key buttons do you want to monitor?
# up, down, left, right, escape
(key_up, key_down, key_left, key_right, key_escape)= (273, 274, 276, 275, 27)

# initialize objects
sp = bird.Bird()
lastTick = pygame.time.get_ticks()

# Event Handler method
def handleEvents():
	# Handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT: 
			sys.exit(0) 
		elif event.type == pygame.KEYDOWN:
			if event.key == key_escape:
				sys.exit(0)
			elif event.key == key_up:
				sp.setContinuousFlapping(0.)
		elif event.type == pygame.KEYUP:
			if event.key == key_up:
				sp.setContinuousFlapping(100.)

while True:
	# Handle events
	handleEvents()
	# Update locations
	newTick = pygame.time.get_ticks()
	sp.update(newTick - lastTick, wingGravity=40.)
	lastTick = newTick
	# Clear screen
	window.fill(black)
	# Draw birds
	sp.draw(window, bodyRadius=10., wingRadius=15.)
	pygame.display.flip()

