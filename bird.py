import math
import pygame

# Set up our colors
white = (255, 255, 255)
gray = (200, 200, 200)

# Threshold for zero (epsilon)
eps = 0.00001

class Bird:

	def __init__(self, pos0 = (320., 240.), speed0 = (0., 0.), 
							rot0 = 0., spin0 = 0.):
		self.pos = pos0
		self.speed = speed0
		self.rot = rot0
		self.spin = spin0
		self.flapAngle = 0.
		self.flapSpeed = 0.
		self.keepFlapping = 0.

	# drawBird function - draws a bird haha
	def draw(self, window, bodyRadius=7, wingRadius=10, sharpAngle=math.pi/6,
			bottomColor=white, topColor=gray):
		# params
		(x, y) = self.pos
		(sx, sy) = self.speed
		offAngle = math.pi - sharpAngle
		speedMag = math.pow(math.pow(x,2) + math.pow(y,2), 0.5)
		wingAngle = math.pi - self.flapAngle
		# compute vertices
		nose = (x + bodyRadius*math.cos(self.rot) + sx, # Nose 
				y + bodyRadius*math.sin(self.rot) + sy)
		rtail = (x + bodyRadius*math.cos(self.rot-offAngle), # Right Side
				y + bodyRadius*math.sin(self.rot-offAngle))
		ltail = (x + bodyRadius*math.cos(self.rot+offAngle), # Left Side
				y + bodyRadius*math.sin(self.rot+offAngle))
		neck = (x + bodyRadius*0.8*math.cos(self.rot), # Nose 
				y + bodyRadius*0.8*math.sin(self.rot))
		rwing = (x + wingRadius*math.cos(self.rot-wingAngle), # Right Side
				y + wingRadius*math.sin(self.rot-wingAngle))
		lwing = (x + wingRadius*math.cos(self.rot+wingAngle), # Left Side
				y + wingRadius*math.sin(self.rot+wingAngle))
		# pack 'em up
		body = [nose, rtail, ltail]
		wings = [neck, rwing, lwing]

		pygame.draw.polygon(window, bottomColor, body)
		pygame.draw.polygon(window, topColor, wings)

	# Move around
	def update(self, interval, wingGravity=1.):
		# Update location
		(x, y) = self.pos
		(sx, sy) = self.speed
		self.pos = (x + sx * interval / 1000., y + sy * interval / 1000.)
		# Update orientation
		self.rot = self.rot + 2. * math.pi * self.spin * interval / 1000.
		# Update flap dampening
		if self.flapAngle > 0.:
			self.flapSpeed = self.flapSpeed - wingGravity * interval / 1000.
		elif self.flapAngle < 0:
			self.flapAngle = 0.
			self.flapSpeed = 0.
		self.flapAngle = self.flapAngle + self.flapSpeed * interval / 1000.
		# Update flap driving
		self.updateFlapMotion(interval)

	def setContinuousFlapping(self, flapStrength=1.):
		self.keepFlapping = flapStrength
		#print "setFlapper to " + flapStrength

	def updateFlapMotion(self, interval):
		if self.flapAngle > math.pi/2 or self.keepFlapping != 0:
			self.flapSpeed = self.flapSpeed + \
				self.keepFlapping*math.cos(self.flapAngle)*interval/1000.

	def isFlapping(self):
		return self.flapAngle == 0.

	# Start a flap
	def flap(self, flapStrength=1.):
		if self.flapAngle < 5*math.pi/6:
			self.flapSpeed = self.flapSpeed + flapStrength