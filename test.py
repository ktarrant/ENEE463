import sys
import math
import bird
#import and init pygame
import pygame
import controls

pygame.init()
#create the screen
size = (sx, sy) = (1200, 800)
window = pygame.display.set_mode(size)

# colors
red = (200, 0 ,0)
black = (0, 0, 0)

def screenWrap(pos):
	(x, y) = pos
	(sx, sy) = size
	if x > sx: x = 0
	elif x < 0: x = sx
	if y > sy: y = 0
	elif y < 0: y = sy
	return (x, y)

def drawTarget(window, target):
	pygame.draw.circle(window, red, target, 3)

# initialize objects
birdFactory = bird.BirdFactory()
# Set up character
birdMan = birdFactory.createBird(1.)
birdMan.pos = (320, 240)
birdMan.ang = math.pi
# set up birdList and AI
birdList = []
bc = bird.BirdAI()
# time and state variables
lastTick = pygame.time.get_ticks()
target = (310, 240)
bc.setGoal({"target": target})
# user controls
controller = controls.Controller()
controller.controls["visc"] = (pygame.K_q, pygame.K_a, # tag, Up/Down keys
		lambda v:v+0.00001, lambda v:v-0.00001, # Up/Down functions
		lambda v:"Viscosity (Q+,A-): %f" % v, 0.00005) # Format func and param
controller.controls["birds"] = (pygame.K_e, pygame.K_d, # tag, Up/Down keys
		lambda bL: bL if bL.append(bird.BirdFactory().
			createBird(1., (sx/2, sy/2))) else bL,
		lambda bL: bL if (bL.pop() if len(bL) > 0 else False) else bL,
		lambda bL:"# of Birds (E+,D-): %d" % (len(bL)+1), birdList)

while True:
	# Update interval
	newTick = pygame.time.get_ticks()
	interval = newTick - lastTick
	lastTick = newTick
	# Handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT: 
			sys.exit(0)
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				sys.exit(0)
			elif event.key == pygame.K_r:
				state = birdMan.getBirdState()
				birdMan = birdFactory.createBird(1.)
				birdMan.setBirdState(state)
			controller.handleEvent(event)
	# Update viscosity
	viscosity = controller.getParam("visc")
	# Clear screen
	window.fill(black)
	# Update character
	bc.manualControl(birdMan)
	birdMan.update(interval, viscosity)
	birdMan.pos = screenWrap(birdMan.pos)
	birdMan.draw(window)
	# Draw target
	drawTarget(window, target)
	# Update birds
	for b in birdList:
		bc.updateAI(b, interval, viscosity)
		b.update(interval, viscosity)
		# Screen wrap
		b.pos = screenWrap(b.pos)
		# draw bird
		b.draw(window)
		#TODO: Get bird percentiles, achievements, names, rankings
	# Add custom messages to the controller view here
	bq = int(birdMan.species["percentile"]*100)
	controller.lines.append("Bird Quality: %.2f/100. " % bq + 
		"Press R to spawn a new bird.")
	# Draw info text
	controller.draw(window)
	pygame.display.flip()

